"""Graph index query client.

Loads graph_index.json v2.0 and provides N-hop BFS, term search,
path finding, orphan detection, and impact analysis.
"""
from __future__ import annotations

import json
import logging
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    from mempalace_client import MemorySnippet
except ImportError:
    @dataclass
    class MemorySnippet:  # type: ignore[no-redef]
        id: str
        source: str
        body: str
        metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphQueryResult:
    center_node: dict
    neighbors: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    hop_depth: int = 0


def load_graph_index(project_root: str) -> dict | None:
    """Load graph_index.json. None if missing or corrupt."""
    path = Path(project_root) / ".claude" / "memory" / "graph" / "graph_index.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "nodes" not in data:
            return None
        return data
    except (json.JSONDecodeError, OSError):
        return None


def _build_node_map(graph: dict) -> dict[str, dict]:
    """local_id -> node dict mapping."""
    return {n["local_id"]: n for n in graph.get("nodes", [])}


def find_node(graph: dict, node_id: str) -> dict | None:
    """Exact match by node ID."""
    return _build_node_map(graph).get(node_id)


def find_by_term(graph: dict, term: str) -> list[dict]:
    """Term search in glossary nodes (title + aliases). Case-insensitive, partial match."""
    results = []
    term_lower = term.lower()
    for node in graph.get("nodes", []):
        if node.get("type") != "glossary":
            continue
        title = node.get("title", "").lower()
        aliases = [t.lower() for t in node.get("tags", [])]
        if (term_lower in title
                or term_lower in " ".join(aliases)
                or any(term_lower in a for a in aliases)):
            results.append(node)
    return results


def get_neighbors(
    graph: dict,
    node_id: str,
    *,
    hop: int = 2,
    edge_types: list[str] | None = None,
) -> GraphQueryResult | None:
    """N-hop BFS neighbor traversal."""
    node_map = _build_node_map(graph)
    center = node_map.get(node_id)
    if center is None:
        return None

    visited: set[str] = {node_id}
    queue: deque[tuple[str, int]] = deque()
    neighbors: list[dict] = []
    edges: list[dict] = []
    max_depth_reached = 0

    def _enqueue_from(node: dict, depth: int) -> None:
        for e in node.get("edges_out", []):
            if edge_types and e["type"] not in edge_types:
                continue
            target = e["target_local"]
            if target not in visited:
                queue.append((target, depth))
                edges.append(e)
        for e in node.get("edges_in", []):
            if edge_types and e["type"] not in edge_types:
                continue
            source = e["source_local"]
            if source not in visited:
                queue.append((source, depth))
                edges.append(e)

    _enqueue_from(center, 1)

    while queue:
        current_id, depth = queue.popleft()
        if current_id in visited or depth > hop:
            continue
        visited.add(current_id)
        max_depth_reached = max(max_depth_reached, depth)

        current_node = node_map.get(current_id)
        if current_node:
            neighbors.append(current_node)
            if depth < hop:
                _enqueue_from(current_node, depth + 1)

    return GraphQueryResult(
        center_node=center,
        neighbors=neighbors,
        edges=edges,
        hop_depth=max_depth_reached,
    )


def find_path(
    graph: dict, source_id: str, target_id: str, *, max_depth: int = 5,
) -> list[dict] | None:
    """BFS shortest path. None if no path exists."""
    node_map = _build_node_map(graph)
    if source_id not in node_map or target_id not in node_map:
        return None

    visited: set[str] = {source_id}
    queue: deque[tuple[str, list[str]]] = deque([(source_id, [source_id])])

    while queue:
        current_id, path = queue.popleft()
        if len(path) > max_depth + 1:
            continue

        current_node = node_map.get(current_id)
        if not current_node:
            continue

        for e in current_node.get("edges_out", []):
            next_id = e.get("target_local")
            if not next_id or next_id in visited:
                continue
            new_path = path + [next_id]
            if next_id == target_id:
                return [node_map[nid] for nid in new_path if nid in node_map]
            visited.add(next_id)
            queue.append((next_id, new_path))

        for e in current_node.get("edges_in", []):
            next_id = e.get("source_local")
            if not next_id or next_id in visited:
                continue
            new_path = path + [next_id]
            if next_id == target_id:
                return [node_map[nid] for nid in new_path if nid in node_map]
            visited.add(next_id)
            queue.append((next_id, new_path))

    return None


def get_orphan_nodes(graph: dict) -> list[dict]:
    """Nodes with zero edges (no edges_out and no edges_in)."""
    return [
        n for n in graph.get("nodes", [])
        if not n.get("edges_out") and not n.get("edges_in")
    ]


def get_domain_subgraph(graph: dict, domain: str) -> dict:
    """Extract nodes + edges for a specific domain."""
    domain_nodes = [n for n in graph.get("nodes", []) if n.get("domain") == domain]
    domain_ids = {n["local_id"] for n in domain_nodes}
    result_nodes = []
    for n in domain_nodes:
        node_copy = dict(n)
        node_copy["edges_out"] = [e for e in n.get("edges_out", []) if e["target_local"] in domain_ids]
        node_copy["edges_in"] = [e for e in n.get("edges_in", []) if e["source_local"] in domain_ids]
        result_nodes.append(node_copy)
    return {"nodes": result_nodes, "namespace": graph.get("namespace", {})}


def graph_result_to_snippets(result: GraphQueryResult) -> list[MemorySnippet]:
    """GraphQueryResult -> list of MemorySnippet for rerank pipeline."""
    snippets = []
    center = result.center_node
    for neighbor in result.neighbors:
        edge_info = ""
        for e in result.edges:
            t = e.get("target_local", "")
            s = e.get("source_local", "")
            if t == neighbor["local_id"] or s == neighbor["local_id"]:
                edge_info = f"{e.get('type', 'related_to')}: {e.get('annotation', '')}"
                break

        body = f"{center['title']} -> {neighbor['title']}\n{edge_info}"
        snippets.append(MemorySnippet(
            id=neighbor["local_id"],
            source="graph",
            body=body,
            metadata={
                "fqn": neighbor.get("fqn", ""),
                "type": neighbor.get("type", ""),
                "domain": neighbor.get("domain", ""),
                "edge": edge_info,
            },
        ))
    return snippets
