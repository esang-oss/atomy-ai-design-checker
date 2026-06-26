"""Build deterministic project diagnosis findings from local files."""
from __future__ import annotations

import json
import logging
import re
from collections import Counter
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any

import yaml


logger = logging.getLogger(__name__)

MISTAKE_THRESHOLD = 3
_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
_CATEGORY_ORDER = {"cleanup": 0, "next_action": 1, "efficiency": 2}
_CF_RE = re.compile(r"CF-[A-Z0-9-]+")
_H2_RE = re.compile(r"^##\s+.*?중단 지점.*$", re.MULTILINE)
_OPEN_TASK_RE = re.compile(r"^\s*-\s*\[\s*\]\s*(.+)\s*$")
_WORD_RE = re.compile(r"[A-Za-z가-힣][A-Za-z0-9가-힣_-]*")


@dataclass(frozen=True)
class Finding:
    category: str
    severity: str
    title: str
    detail: str
    evidence_ref: str
    suggestion: str
    rule_id: str
    confidence: str


@dataclass(frozen=True)
class DiagnosisModel:
    findings: list[Finding]
    counts: dict
    coverage_note: str
    generated_from: dict


def rules_cleanup(signals: dict) -> list[Finding]:
    out: list[Finding] = []
    for path in signals.get("superseded_specs", []):
        out.append(
            Finding(
                "cleanup",
                "medium",
                "폐기 표시된 spec",
                f"{path} 가 status: superseded 입니다.",
                path,
                "아카이브 또는 삭제를 검토하세요.",
                "superseded_spec",
                "high",
            )
        )
    for path in signals.get("draft_specs", []):
        out.append(
            Finding(
                "cleanup",
                "low",
                "중단된 draft spec",
                f"{path} 가 미완 draft 입니다.",
                path,
                "이어가기 또는 폐기를 결정하세요.",
                "stalled_draft_spec",
                "high",
            )
        )
    for task in signals.get("deferred_tasks", []):
        out.append(
            Finding(
                "cleanup",
                "low",
                "보류된 작업",
                task,
                "docs/plan.md",
                "검토만 하세요(외부 차단/의도 보류일 수 있어 삭제 대상 아님).",
                "deferred_task",
                "high",
            )
        )
    for sha in signals.get("broken_test_shas", []):
        out.append(
            Finding(
                "cleanup",
                "low",
                "broken-test 커밋 흔적",
                "reflog 에 broken-test 마커 커밋이 있습니다.",
                sha,
                "후속 정리/amend 여부를 확인하세요.",
                "broken_test_commit",
                "low",
            )
        )
    return out


def rules_next_action(signals: dict) -> list[Finding]:
    out: list[Finding] = []
    carry = signals.get("carry_forward", {})
    cf_tokens = sorted(set(carry.get("cf_tokens", [])))
    if carry.get("unresolved") or cf_tokens:
        token_text = ", ".join(cf_tokens) if cf_tokens else "unresolved_findings"
        out.append(
            Finding(
                "next_action",
                "high",
                "열린 carry-forward",
                f"최신 context 블록에 열린 carry-forward 가 있습니다: {token_text}",
                "docs/context.md",
                "다음 작업 전에 우선 해소 또는 명시적 override 를 결정하세요.",
                "open_carry_forward",
                "high",
            )
        )
    for task in signals.get("incomplete_roadmap", []):
        out.append(
            Finding(
                "next_action",
                "medium",
                "미완료 로드맵 Task",
                task,
                "docs/plan.md",
                "우선순위가 맞는지 검토하고 다음 실행 후보로 유지하세요.",
                "incomplete_roadmap",
                "high",
            )
        )
    timeline = signals.get("timeline", {})
    if timeline.get("mode") == "digest" and int(timeline.get("context_blocks", 0) or 0) <= 2:
        out.append(
            Finding(
                "next_action",
                "low",
                "기록 coverage 낮음",
                "timeline 이 digest 모드이고 context 블록이 적습니다.",
                "timeline_index.json",
                "진단 신뢰도 제한을 표시하고 한 번 더 handoff 기록을 쌓으세요.",
                "coverage_gap",
                "high",
            )
        )
    return out


def rules_efficiency(signals: dict) -> list[Finding]:
    clusters = {
        token: count
        for token, count in sorted(signals.get("recurring_mistakes", {}).items())
        if count >= MISTAKE_THRESHOLD
    }
    if not clusters:
        return []
    detail = ", ".join(f"{token}={count}" for token, count in clusters.items())
    return [
        Finding(
            "efficiency",
            "medium",
            "반복 실수 패턴",
            f"recurring-mistakes 에 반복 클러스터가 있습니다: {detail}",
            ".claude/memory/learnings/recurring-mistakes.md",
            "테스트/체크리스트/리뷰 순서 중 하나를 프로세스 가드로 보강하세요.",
            "recurring_mistake_cluster",
            "high",
        )
    ]


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        logger.warning("frontmatter parse failed: %s", exc)
        return {}
    return data if isinstance(data, dict) else {}


def latest_carry_forward(context_md_text: str) -> dict:
    block = _latest_context_block(context_md_text)
    lower = block.lower()
    unresolved = "unresolved_findings: true" in lower or "closure_status: compliance_blocked" in lower
    return {"unresolved": unresolved, "cf_tokens": sorted(set(_CF_RE.findall(block)))}


def collect_signals(project_root: str, timeline_model: dict) -> dict:
    root = Path(project_root)
    timeline = _coverage_dict(timeline_model)
    signals = {
        "superseded_specs": _scan_specs(root)[0],
        "draft_specs": _scan_specs(root)[1],
        "deferred_tasks": [],
        "incomplete_roadmap": [],
        "carry_forward": {"unresolved": False, "cf_tokens": []},
        "recurring_mistakes": _scan_recurring(root),
        "broken_test_shas": _scan_reflog(root),
        "timeline": timeline,
    }
    deferred, incomplete = _scan_plan(root)
    signals["deferred_tasks"] = deferred
    signals["incomplete_roadmap"] = incomplete
    context = _read_text(root / "docs" / "context.md")
    if context:
        signals["carry_forward"] = latest_carry_forward(context)
    return signals


def build_diagnosis(project_root: str) -> DiagnosisModel:
    root = Path(project_root)
    timeline_model = _build_timeline_snapshot(project_root)
    signals = collect_signals(project_root, timeline_model)
    findings = rules_cleanup(signals) + rules_next_action(signals) + rules_efficiency(signals)
    findings = sorted(findings, key=_finding_key)
    counts = _count_findings(findings)
    coverage_note = _coverage_note(findings, signals)
    model = DiagnosisModel(findings, counts, coverage_note, _generated_from(root, signals, timeline_model))
    _persist_index(root, model)
    return model


def _scan_specs(root: Path) -> tuple[list[str], list[str]]:
    superseded: list[str] = []
    drafts: list[str] = []
    for path in sorted((root / "docs" / "specs").glob("*.md")):
        rel = _rel(root, path)
        if path.name.endswith(".draft.md"):
            drafts.append(rel)
        frontmatter = parse_frontmatter(_read_text(path))
        if str(frontmatter.get("status", "")).lower() == "superseded":
            superseded.append(rel)
    return superseded, drafts


def _scan_plan(root: Path) -> tuple[list[str], list[str]]:
    deferred: list[str] = []
    incomplete: list[str] = []
    for line in _read_text(root / "docs" / "plan.md").splitlines():
        match = _OPEN_TASK_RE.match(line)
        if not match:
            continue
        task = match.group(1).strip()
        if "*(Deferred" in task or "Deferred" in task:
            deferred.append(task)
        else:
            incomplete.append(task)
    return deferred, incomplete


def _scan_recurring(root: Path) -> dict[str, int]:
    text = _read_text(root / ".claude" / "memory" / "learnings" / "recurring-mistakes.md")
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        if not line.lstrip().startswith("- ["):
            continue
        for token in _WORD_RE.findall(line.lower()):
            if token not in {"the", "and", "with"} and len(token) >= 3:
                counts[token] += 1
    return dict(counts)


def _scan_reflog(root: Path) -> list[str]:
    shas: list[str] = []
    for line in _read_text(root / ".git" / "logs" / "HEAD").splitlines()[-50:]:
        sha = _reflog_new_sha(line)
        subject = line.split("\t", 1)[1].lower() if "\t" in line else ""
        if sha and _is_broken_test_subject(subject):
            shas.append(sha[:7])
    return shas


def _is_broken_test_subject(subject: str) -> bool:
    clean = subject.replace("commit:", "", 1).strip()
    return bool(re.search(r"(^|\s)(broken-test|wip-broken)(\s|$)", clean) or clean == "broken")


def _reflog_new_sha(line: str) -> str:
    parts = line.split()
    return parts[1] if len(parts) >= 2 and re.fullmatch(r"[0-9a-fA-F]+", parts[1]) else ""


def _latest_context_block(text: str) -> str:
    matches = list(_H2_RE.finditer(text))
    if not matches:
        return text
    start = matches[0].start()
    end = matches[1].start() if len(matches) > 1 else len(text)
    return text[start:end]


def _coverage_dict(timeline_model: dict) -> dict:
    coverage = timeline_model.get("coverage", {}) if isinstance(timeline_model, dict) else {}
    return coverage if isinstance(coverage, dict) else {}


def _build_timeline_snapshot(project_root: str) -> dict:
    try:
        import timeline_builder

        model = timeline_builder.build_timeline(project_root)
    except Exception as exc:
        logger.warning("timeline build failed during diagnosis: %s", exc)
        return {"coverage": {}}
    if model is None:
        return {"coverage": {}}
    coverage = asdict(model.coverage) if is_dataclass(model.coverage) else vars(model.coverage)
    return {"coverage": coverage, "cycles": len(getattr(model, "cycles", []))}


def _finding_key(finding: Finding) -> tuple:
    return (
        _SEVERITY_ORDER.get(finding.severity, 9),
        _CATEGORY_ORDER.get(finding.category, 9),
        finding.rule_id,
        finding.evidence_ref,
    )


def _count_findings(findings: list[Finding]) -> dict:
    by_category = Counter(f.category for f in findings)
    by_severity = Counter(f.severity for f in findings)
    return {
        "cleanup": by_category.get("cleanup", 0),
        "next_action": by_category.get("next_action", 0),
        "efficiency": by_category.get("efficiency", 0),
        "total": len(findings),
        "by_severity": dict(sorted(by_severity.items())),
    }


def _coverage_note(findings: list[Finding], signals: dict) -> str:
    if not findings:
        return "clean (신호 없음)"
    return "limited (timeline digest)" if signals.get("timeline", {}).get("mode") == "digest" else "full"


def _generated_from(root: Path, signals: dict, timeline_model: dict) -> dict:
    return {
        "timeline_cycles": int(timeline_model.get("cycles", 0) or 0),
        "has_plan": (root / "docs" / "plan.md").exists(),
        "has_context": (root / "docs" / "context.md").exists(),
        "has_reflog": (root / ".git" / "logs" / "HEAD").exists(),
        "signals": {key: bool(value) for key, value in signals.items() if key != "timeline"},
    }


def _persist_index(root: Path, model: DiagnosisModel) -> None:
    out = root / ".claude" / "memory" / "graph" / "views" / "diagnosis_index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(asdict(model), ensure_ascii=False, indent=2), encoding="utf-8")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
