"""Build a deterministic project timeline model from local project records."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Utterance:
    ts: str
    text: str
    category: str


@dataclass(frozen=True)
class TimelineCycle:
    cycle_key: str
    date: str
    ordinal: int
    session_key: str | None
    title: str
    summary: str
    decisions: list[dict]
    utterances: list[Utterance]
    outputs: str
    next_task: str
    coverage: dict


@dataclass(frozen=True)
class RoadmapState:
    done: list[str]
    remaining: list[str]
    current_phase: str


@dataclass(frozen=True)
class Coverage:
    context_blocks: int
    decision_nodes: int
    utterances: int
    roadmap_items: int
    mode: str


@dataclass(frozen=True)
class TimelineModel:
    cycles: list[TimelineCycle]
    roadmap: RoadmapState
    coverage: Coverage
    warnings: list[str]


_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_CTX_HEADER_RE = re.compile(
    r"^##\s*(?:🔖\s*)?중단 지점\s*[—-]\s*(?P<date>\d{4}-\d{2}-\d{2})\s*(?:\((?P<title>.*)\))?\s*$"
)
_ANY_DATED_H2_RE = re.compile(
    r"^##\s+.*?(?P<date>\d{4}-\d{2}-\d{2})\s*(?:\((?P<title>.*)\))?\s*$"
)
_ROADMAP_DONE_RE = re.compile(r"^\s*-\s*\[x\]\s*(.+)\s*$", re.IGNORECASE)
_ROADMAP_OPEN_RE = re.compile(r"^\s*-\s*\[\s*\]\s*(.+)\s*$")
_UTTERANCE_RE = re.compile(r"^-\s*\[([^\]]+)\]\s*\(([^)]*)\)\s*(.+)$")


def parse_context_blocks(text: str) -> list[dict]:
    """Parse handoff context blocks in document order."""
    lines = text.splitlines()
    starts: list[tuple[int, re.Match[str]]] = []
    for idx, line in enumerate(lines):
        match = _CTX_HEADER_RE.match(line) or _fallback_context_header(line)
        if match:
            starts.append((idx, match))

    date_counts: dict[str, int] = {}
    blocks: list[dict] = []
    for pos, (start, match) in enumerate(starts):
        end = starts[pos + 1][0] if pos + 1 < len(starts) else len(lines)
        date = match.group("date")
        title = (match.groupdict().get("title") or "").strip()
        ordinal = date_counts.get(date, 0)
        date_counts[date] = ordinal + 1
        body = lines[start + 1:end]
        blocks.append(
            {
                "date": date,
                "ordinal": ordinal,
                "title": title,
                "summary": _extract_section(body, "summary"),
                "next_task": _extract_section(body, "next_task", strip_blockquote=True),
            }
        )
    return blocks


def parse_roadmap(plan_md_text: str) -> RoadmapState:
    """Parse checked and unchecked roadmap items."""
    done: list[str] = []
    remaining: list[str] = []
    current_phase = ""

    for line in plan_md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### Phase"):
            current_phase = stripped.lstrip("#").strip()
            continue
        match_done = _ROADMAP_DONE_RE.match(line)
        if match_done:
            done.append(match_done.group(1).strip())
            continue
        match_open = _ROADMAP_OPEN_RE.match(line)
        if match_open:
            remaining.append(match_open.group(1).strip())

    return RoadmapState(done=done, remaining=remaining, current_phase=current_phase)


def scan_memory_cycles(memory_dir: str | Path) -> tuple[list[dict], list[str]]:
    """Scan ASMR memory markdown files without assuming strict frontmatter."""
    root = Path(memory_dir)
    warnings: list[str] = []
    nodes: list[dict] = []
    categories = ["decisions", "architecture", "bugs", "learnings", "compliance-audit"]

    if not root.exists():
        return [], [f"memory dir missing: {root}"]

    for category in categories:
        folder = root / category
        if not folder.exists():
            warnings.append(f"{category} missing")
            continue
        for path in sorted(folder.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                warnings.append(f"{path}: {exc}")
                continue
            fm, body = _split_frontmatter(text)
            date = fm.get("date") or _date_from_text(path.name) or _date_from_text(body) or ""
            title = (
                fm.get("title")
                or fm.get("id")
                or fm.get("session")
                or _title_from_filename(path.stem)
            )
            nodes.append(
                {
                    "id": fm.get("id", ""),
                    "title": str(title),
                    "date": str(date),
                    "type": category,
                    "domain": fm.get("domain", ""),
                    "session_key": fm.get("session", ""),
                    "source": str(path),
                }
            )

    return nodes, warnings


def load_utterances(project_root: str | Path, cycle: dict) -> tuple[list[Utterance], list[str]]:
    """Load user utterances from memtemple drawers by direct file parsing."""
    warnings: list[str] = []
    try:
        import mempalace_client
    except Exception as exc:
        return [], [f"memtemple unavailable: {exc}"]

    if not mempalace_client.is_available():
        return [], ["memtemple unavailable: utterances skipped"]

    drawer_dir = _drawer_dir(project_root)
    if not drawer_dir.exists():
        return [], [f"memtemple drawer dir missing: {drawer_dir}"]

    utterances: list[Utterance] = []
    cycle_date = str(cycle.get("date", ""))
    for path in sorted(drawer_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            warnings.append(f"{path}: {exc}")
            continue
        if cycle_date and cycle_date not in path.name and cycle_date not in text:
            continue
        utterances.extend(_parse_utterance_section(text))

    return utterances, warnings


def build_timeline(project_root: str) -> TimelineModel | None:
    """Scan all supported sources and persist a timeline index."""
    root = Path(project_root)
    warnings: list[str] = []

    context_path = root / "docs" / "context.md"
    if context_path.exists():
        try:
            context_blocks = parse_context_blocks(context_path.read_text(encoding="utf-8"))
        except OSError as exc:
            context_blocks = []
            warnings.append(f"{context_path}: {exc}")
    else:
        context_blocks = []
        warnings.append("docs/context.md missing")

    plan_path = root / "docs" / "plan.md"
    if plan_path.exists():
        try:
            roadmap = parse_roadmap(plan_path.read_text(encoding="utf-8"))
        except OSError as exc:
            roadmap = RoadmapState([], [], "")
            warnings.append(f"{plan_path}: {exc}")
    else:
        roadmap = RoadmapState([], [], "")
        warnings.append("docs/plan.md missing")

    memory_nodes, memory_warnings = scan_memory_cycles(root / ".claude" / "memory")
    warnings.extend(memory_warnings)

    block_cycles = [_cycle_from_context_block(block) for block in context_blocks]
    cycles_by_key = {(c.date, c.ordinal): c for c in block_cycles}
    date_counts: dict[str, int] = {}
    for block in context_blocks:
        date_counts[block["date"]] = max(date_counts.get(block["date"], 0), block["ordinal"] + 1)

    nodes_by_key: dict[tuple[str, int], list[dict]] = {key: [] for key in cycles_by_key}
    for node in memory_nodes:
        date = str(node.get("date", ""))
        if not date:
            continue
        key = _best_cycle_key_for_date(date, cycles_by_key, date_counts)
        if key not in cycles_by_key:
            cycles_by_key[key] = TimelineCycle(
                cycle_key=f"{key[0]}#{key[1]}",
                date=key[0],
                ordinal=key[1],
                session_key=node.get("session_key") or None,
                title=f"Memory records — {key[0]}",
                summary="",
                decisions=[],
                utterances=[],
                outputs="",
                next_task="",
                coverage={},
            )
        nodes_by_key.setdefault(key, []).append(node)

    final_cycles: list[TimelineCycle] = []
    utterance_count = 0
    for key in sorted(cycles_by_key):
        base = cycles_by_key[key]
        utterances, utter_warnings = load_utterances(str(root), {"date": base.date, "ordinal": base.ordinal})
        warnings.extend(utter_warnings)
        utterance_count += len(utterances)
        decisions = nodes_by_key.get(key, [])
        coverage = {
            "has_decisions": bool(decisions),
            "has_utterances": bool(utterances),
            "has_context": key in {(b["date"], b["ordinal"]) for b in context_blocks},
            "source_counts": {"memory": len(decisions), "utterances": len(utterances)},
        }
        final_cycles.append(
            TimelineCycle(
                cycle_key=base.cycle_key,
                date=base.date,
                ordinal=base.ordinal,
                session_key=base.session_key,
                title=base.title,
                summary=base.summary,
                decisions=decisions,
                utterances=utterances,
                outputs=base.outputs,
                next_task=base.next_task,
                coverage=coverage,
            )
        )

    roadmap_items = len(roadmap.done) + len(roadmap.remaining)
    if not final_cycles and not memory_nodes and utterance_count == 0 and roadmap_items == 0:
        return None

    coverage = Coverage(
        context_blocks=len(context_blocks),
        decision_nodes=len(memory_nodes),
        utterances=utterance_count,
        roadmap_items=roadmap_items,
        mode="digest" if len(memory_nodes) == 0 and utterance_count == 0 else "full",
    )
    model = TimelineModel(final_cycles, roadmap, coverage, warnings)
    _persist_index(root, model)
    return model


def _fallback_context_header(line: str) -> re.Match[str] | None:
    if not line.startswith("## "):
        return None
    if "Phase" in line and "중단" not in line:
        return None
    return _ANY_DATED_H2_RE.match(line)


def _extract_section(lines: list[str], kind: str, *, strip_blockquote: bool = False) -> str:
    selected: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## "):
            break
        if line.startswith("### "):
            header = line.strip("# ").strip()
            if kind == "summary":
                in_section = ("이번" in header and "요약" in header) or "cycle" in header.lower()
            else:
                in_section = ("다음" in header and "Task" in header) or (
                    "Task" in header and "cycle" not in header.lower()
                )
            continue
        if in_section:
            selected.append(_strip_blockquote(line) if strip_blockquote else line)
    return "\n".join(line for line in selected).strip()


def _strip_blockquote(line: str) -> str:
    return line.lstrip().removeprefix(">").strip()


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm, parts[2]


def _date_from_text(text: str) -> str | None:
    match = _DATE_RE.search(text)
    return match.group(0) if match else None


def _title_from_filename(stem: str) -> str:
    return stem.replace("_", " ").replace("-", " ").strip()


def _drawer_dir(project_root: str | Path) -> Path:
    try:
        import mempalace_client

        vault = Path(mempalace_client.get_palace_home())
        wing = Path(project_root).resolve().name
        return vault / wing / "sessions"
    except Exception:
        return Path(project_root) / "sessions"


def _parse_utterance_section(text: str) -> list[Utterance]:
    lines = text.splitlines()
    in_section = False
    utterances: list[Utterance] = []
    for line in lines:
        if line.startswith("## "):
            in_section = line.strip().lower() == "## user utterances"
            continue
        if not in_section:
            continue
        match = _UTTERANCE_RE.match(line.strip())
        if match:
            utterances.append(
                Utterance(ts=match.group(1).strip(), category=match.group(2).strip(), text=match.group(3).strip())
            )
    return utterances


def _cycle_from_context_block(block: dict[str, Any]) -> TimelineCycle:
    date = str(block["date"])
    ordinal = int(block["ordinal"])
    return TimelineCycle(
        cycle_key=f"{date}#{ordinal}",
        date=date,
        ordinal=ordinal,
        session_key=None,
        title=str(block.get("title", "")),
        summary=str(block.get("summary", "")),
        decisions=[],
        utterances=[],
        outputs="",
        next_task=str(block.get("next_task", "")),
        coverage={},
    )


def _best_cycle_key_for_date(
    date: str,
    cycles_by_key: dict[tuple[str, int], TimelineCycle],
    date_counts: dict[str, int],
) -> tuple[str, int]:
    existing = sorted(key for key in cycles_by_key if key[0] == date)
    if existing:
        return existing[0]
    ordinal = date_counts.get(date, 0)
    date_counts[date] = ordinal + 1
    return date, ordinal


def _persist_index(root: Path, model: TimelineModel) -> None:
    out = root / ".claude" / "memory" / "graph" / "views" / "timeline_index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(asdict(model), ensure_ascii=False, indent=2), encoding="utf-8")
