"""ASMR memory + glossary -> graph_index.json v2.0 build.

All failures are recorded in BuildResult. Never blocks /handoff.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

import frontmatter

logger = logging.getLogger(__name__)

# [[target]] or [[target|edge_type]]
_WIKILINK_RE = re.compile(r"\[\[([A-Za-z0-9_:*/-]+)(?:\|([a-z_]+))?\]\]")

EDGE_TYPES = {
    "depends_on", "derived_from", "contradicts", "extends",
    "related_to", "defines", "supersedes", "measured_by", "based_on",
}

REVERSE_EDGE_MAP = {
    "depends_on": "depended_by",
    "derived_from": "gave_rise_to",
    "extends": "extended_by",
    "defines": "defined_by",
    "supersedes": "superseded_by",
    "measured_by": "measures",
    "based_on": "informed",
    "contradicts": "contradicts",
    "related_to": "related_to",
}

ASMR_CATEGORIES = ["decisions", "architecture", "bugs", "learnings"]


@dataclass
class BuildResult:
    nodes_total: int = 0
    edges_total: int = 0
    orphans: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class NodeData:
    local_id: str
    fqn: str
    node_type: str  # memory | glossary | data_source | external | project
    title: str
    source_path: str
    tags: list[str] = field(default_factory=list)
    domain: str = ""
    status: str = "active"
    created: str = ""
    body: str = ""
    references: list[str] = field(default_factory=list)
    superseded_by: str | None = None
    links: list[dict] = field(default_factory=list)


@dataclass
class EdgeData:
    source_local: str
    source_fqn: str
    target_local: str
    target_fqn: str
    edge_type: str
    annotation: str = ""


def _make_fqn(namespace: dict, local_id: str) -> str:
    """Namespace + local ID -> FQN."""
    org = namespace.get("org", "*")
    dept = namespace.get("dept", "*")
    user = namespace.get("user", "*")
    project = namespace.get("project", "*")
    return f"{org}/{dept}/{user}/{project}/{local_id}"


def _resolve_target_fqn(namespace: dict, target_local: str) -> str:
    """Target local ID FQN resolution. glossary: prefix uses project=*."""
    if target_local.startswith("glossary:"):
        org = namespace.get("org", "*")
        dept = namespace.get("dept", "*")
        user = namespace.get("user", "*")
        return f"{org}/{dept}/{user}/*/{target_local}"
    if target_local.startswith("ds:"):
        org = namespace.get("org", "*")
        return f"{org}/*/*/*/{target_local}"
    return _make_fqn(namespace, target_local)


def _scan_memory_files(memory_dir: Path, namespace: dict) -> tuple[list[NodeData], list[str]]:
    """Scan ASMR category directories for memory files. Returns (nodes, warnings)."""
    nodes = []
    warnings = []
    for category in ASMR_CATEGORIES:
        cat_dir = memory_dir / category
        if not cat_dir.exists():
            continue
        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                warnings.append(f"encoding error in {md_file.name}: {exc}")
                logger.warning("Skipping %s: %s", md_file.name, exc)
                continue
            fm, body = frontmatter.parse(content)
            local_id = fm.get("id", "")
            if not local_id:
                continue
            local_id = str(local_id)
            refs = fm.get("references", [])
            if isinstance(refs, str):
                refs = [r.strip() for r in refs.split(",")]
            links = fm.get("links", [])
            if not isinstance(links, list):
                links = []
            tags = fm.get("tags", []) or []
            if not isinstance(tags, list):
                tags = []
            nodes.append(NodeData(
                local_id=local_id,
                fqn=_make_fqn(namespace, local_id),
                node_type="memory",
                title=str(fm.get("title", md_file.stem)),
                source_path=str(md_file.relative_to(memory_dir.parent.parent)),
                tags=tags,
                domain=str(fm.get("domain", "")),
                status=str(fm.get("status", "active")),
                created=str(fm.get("created", "")),
                body=body,
                references=refs if isinstance(refs, list) else [],
                superseded_by=fm.get("superseded_by"),
                links=links,
            ))
    return nodes, warnings


def _scan_glossary_files(glossary_dir: Path, namespace: dict) -> list[NodeData]:
    """Scan glossary/ directory for term files."""
    nodes = []
    if not glossary_dir.exists():
        return nodes
    for md_file in sorted(glossary_dir.glob("*.md")):
        if md_file.name.startswith("_"):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        fm, body = frontmatter.parse(content)
        local_id = fm.get("id", "")
        if not local_id:
            local_id = f"glossary:{md_file.stem}"
        local_id = str(local_id)
        fqn = _resolve_target_fqn(namespace, local_id)
        aliases = fm.get("aliases", []) or []
        if not isinstance(aliases, list):
            aliases = []
        nodes.append(NodeData(
            local_id=local_id,
            fqn=fqn,
            node_type="glossary",
            title=str(fm.get("term", md_file.stem)),
            source_path=str(md_file),
            tags=aliases,
            domain=str(fm.get("domain", "")),
            status=str(fm.get("status", "active")),
            created=str(fm.get("created", "")),
            body=body,
        ))
    return nodes


def _scan_data_sources(sources_dir: Path, namespace: dict) -> list[NodeData]:
    """Scan graph/sources/ directory for data_source YAML files."""
    nodes = []
    if not sources_dir.exists():
        return nodes
    for yaml_file in sorted(sources_dir.glob("*.yaml")):
        try:
            content = yaml_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        parsed = yaml.safe_load(content)
        if not isinstance(parsed, dict):
            continue
        local_id = parsed.get("id", "")
        if not local_id:
            continue
        local_id = str(local_id)
        nodes.append(NodeData(
            local_id=local_id,
            fqn=_resolve_target_fqn(namespace, local_id),
            node_type="data_source",
            title=str(parsed.get("name", yaml_file.stem)),
            source_path=str(yaml_file),
            domain=str(parsed.get("owner_dept", "")),
            status="active",
        ))
    return nodes


def _extract_edges_from_references(node: NodeData, namespace: dict) -> list[EdgeData]:
    """references field -> related_to edges (excludes targets with explicit links)."""
    explicit_targets = {link.get("target") for link in node.links if isinstance(link, dict)}
    edges = []
    for ref in node.references:
        if ref in explicit_targets:
            continue
        edges.append(EdgeData(
            source_local=node.local_id,
            source_fqn=node.fqn,
            target_local=str(ref),
            target_fqn=_resolve_target_fqn(namespace, str(ref)),
            edge_type="related_to",
            annotation="from references field",
        ))
    return edges


def _extract_edges_from_links(node: NodeData, namespace: dict) -> list[EdgeData]:
    """frontmatter links field -> explicit edges."""
    edges = []
    for link in node.links:
        if not isinstance(link, dict):
            continue
        target = link.get("target", "")
        if not target:
            continue
        edge_type = link.get("type", "related_to")
        if edge_type not in EDGE_TYPES:
            edge_type = "related_to"
        edges.append(EdgeData(
            source_local=node.local_id,
            source_fqn=node.fqn,
            target_local=str(target),
            target_fqn=_resolve_target_fqn(namespace, str(target)),
            edge_type=edge_type,
            annotation=link.get("annotation", ""),
        ))
    return edges


def _extract_edges_from_superseded(node: NodeData, namespace: dict) -> list[EdgeData]:
    """superseded_by -> supersedes reverse edge."""
    if not node.superseded_by:
        return []
    target = str(node.superseded_by)
    return [EdgeData(
        source_local=target,
        source_fqn=_resolve_target_fqn(namespace, target),
        target_local=node.local_id,
        target_fqn=node.fqn,
        edge_type="supersedes",
        annotation="superseded_by field",
    )]


def _extract_edges_from_wikilinks(node: NodeData, namespace: dict) -> list[EdgeData]:
    """Body [[wikilink]] parsing -> edges."""
    edges = []
    for match in _WIKILINK_RE.finditer(node.body):
        target = match.group(1)
        edge_type = match.group(2) or "related_to"
        if edge_type not in EDGE_TYPES:
            edge_type = "related_to"
        edges.append(EdgeData(
            source_local=node.local_id,
            source_fqn=node.fqn,
            target_local=target,
            target_fqn=_resolve_target_fqn(namespace, target),
            edge_type=edge_type,
        ))
    return edges


def _extract_glossary_auto_links(
    node: NodeData, glossary_terms: dict[str, str], namespace: dict,
    existing_targets: set[str] | None = None,
) -> list[EdgeData]:
    """Auto-detect glossary terms in body -> related_to edges.

    CEO decision: 3+ occurrences in decision/content section only.
    """
    edges = []
    # Extract decision section only (contains 결정, 내용, Decision, or Content in header)
    body_to_scan = node.body
    for line in node.body.splitlines():
        if line.startswith("## ") and any(
            kw in line for kw in ["결정", "내용", "Decision", "Content"]
        ):
            idx = node.body.find(line)
            if idx >= 0:
                body_to_scan = node.body[idx:]
            break

    if existing_targets is None:
        existing_targets = set()
    body_lower = body_to_scan.lower()
    for term, glossary_id in glossary_terms.items():
        if glossary_id in existing_targets:
            continue
        count = body_lower.count(term.lower())
        if count >= 3:
            edges.append(EdgeData(
                source_local=node.local_id,
                source_fqn=node.fqn,
                target_local=glossary_id,
                target_fqn=_resolve_target_fqn(namespace, glossary_id),
                edge_type="related_to",
                annotation=f"auto-detected: '{term}' appears {count}x in decision section",
            ))
    return edges


def _generate_reverse_edges(edges: list[EdgeData]) -> list[EdgeData]:
    """Forward edges -> reverse backlinks."""
    reverse = []
    for e in edges:
        rev_type = REVERSE_EDGE_MAP.get(e.edge_type, f"{e.edge_type}_reverse")
        reverse.append(EdgeData(
            source_local=e.target_local,
            source_fqn=e.target_fqn,
            target_local=e.source_local,
            target_fqn=e.source_fqn,
            edge_type=rev_type,
            annotation=e.annotation,
        ))
    return reverse


def _deduplicate_edges(edges: list[EdgeData]) -> list[EdgeData]:
    """Deduplicate by (source, target, type)."""
    seen: set[tuple[str, str, str]] = set()
    deduped = []
    for e in edges:
        key = (e.source_local, e.target_local, e.edge_type)
        if key not in seen:
            seen.add(key)
            deduped.append(e)
    return deduped


def _detect_orphans(nodes: list[NodeData], edges: list[EdgeData]) -> list[str]:
    """Nodes with zero edges."""
    connected = set()
    for e in edges:
        connected.add(e.source_local)
        connected.add(e.target_local)
    return [n.local_id for n in nodes if n.local_id not in connected]


def build(project_root: str, session_number: int) -> BuildResult | None:
    """Full graph build. Returns None if graph/ doesn't exist."""
    root = Path(project_root)
    memory_dir = root / ".claude" / "memory"
    graph_dir = memory_dir / "graph"

    if not graph_dir.exists():
        return None

    # Load namespace from graph_meta.yaml
    meta_path = graph_dir / "graph_meta.yaml"
    namespace = {"org": "*", "dept": "*", "user": "*", "project": "*"}
    settings: dict[str, Any] = {}
    if meta_path.exists():
        try:
            meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
            if isinstance(meta, dict):
                ns = meta.get("namespace", {})
                if isinstance(ns, dict):
                    namespace.update(ns)
                settings = meta.get("settings", {}) or {}
        except (yaml.YAMLError, OSError) as exc:
            logger.warning("graph_meta.yaml parse error: %s", exc)

    # Scan nodes
    memory_nodes, scan_warnings = _scan_memory_files(memory_dir, namespace)
    glossary_nodes = _scan_glossary_files(graph_dir / "glossary", namespace)
    ds_nodes = _scan_data_sources(graph_dir / "sources", namespace)
    all_nodes = memory_nodes + glossary_nodes + ds_nodes

    # Build glossary term lookup for auto-detection
    glossary_terms: dict[str, str] = {}
    for gn in glossary_nodes:
        glossary_terms[gn.title.lower()] = gn.local_id
        for alias in gn.tags:
            glossary_terms[alias.lower()] = gn.local_id

    # Extract edges
    all_edges: list[EdgeData] = []
    for node in memory_nodes:
        all_edges.extend(_extract_edges_from_links(node, namespace))
        all_edges.extend(_extract_edges_from_references(node, namespace))
        all_edges.extend(_extract_edges_from_superseded(node, namespace))
        all_edges.extend(_extract_edges_from_wikilinks(node, namespace))
        if settings.get("auto_link_glossary", False):
            already_linked = {e.target_local for e in all_edges if e.source_local == node.local_id}
            all_edges.extend(
                _extract_glossary_auto_links(node, glossary_terms, namespace, already_linked)
            )

    # Deduplicate forward edges
    all_edges = _deduplicate_edges(all_edges)

    # Detect orphans (forward edges only)
    orphans = _detect_orphans(all_nodes, all_edges)

    # Build index structure
    node_edge_map: dict[str, dict] = {}
    for n in all_nodes:
        node_edge_map[n.local_id] = {
            "local_id": n.local_id,
            "fqn": n.fqn,
            "type": n.node_type,
            "title": n.title,
            "source_path": n.source_path,
            "tags": n.tags,
            "domain": n.domain,
            "status": n.status,
            "created": n.created,
            "edges_out": [],
            "edges_in": [],
        }

    for e in all_edges:
        if e.source_local in node_edge_map:
            node_edge_map[e.source_local]["edges_out"].append({
                "target_local": e.target_local,
                "target_fqn": e.target_fqn,
                "type": e.edge_type,
                "annotation": e.annotation,
            })

    # edges_in: populated from forward edges (target node gets an incoming edge)
    for e in all_edges:
        if e.target_local in node_edge_map:
            node_edge_map[e.target_local]["edges_in"].append({
                "source_local": e.source_local,
                "source_fqn": e.source_fqn,
                "type": e.edge_type,
                "annotation": e.annotation,
            })

    # Count edges by type
    edge_type_counts: dict[str, int] = {}
    for e in all_edges:
        edge_type_counts[e.edge_type] = edge_type_counts.get(e.edge_type, 0) + 1

    # Count nodes by type
    nodes_by_type: dict[str, int] = {}
    for n in all_nodes:
        nodes_by_type[n.node_type] = nodes_by_type.get(n.node_type, 0) + 1

    index = {
        "version": "2.0.0",
        "namespace": namespace,
        "built_at": "",
        "built_session": session_number,
        "stats": {
            "total_nodes": len(all_nodes),
            "total_edges": len(all_edges),
            "nodes_by_type": nodes_by_type,
            "edges_by_type": edge_type_counts,
            "orphan_nodes": orphans,
        },
        "nodes": list(node_edge_map.values()),
    }

    # Write
    index_path = graph_dir / "graph_index.json"
    try:
        index_path.write_text(
            json.dumps(index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        logger.warning("Failed to write graph_index.json: %s", exc)
        return BuildResult(
            nodes_total=len(all_nodes),
            edges_total=len(all_edges),
            orphans=orphans,
            warnings=scan_warnings + [f"write failed: {exc}"],
        )

    return BuildResult(
        nodes_total=len(all_nodes),
        edges_total=len(all_edges),
        orphans=orphans,
        warnings=scan_warnings,
    )
