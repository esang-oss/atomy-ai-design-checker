"""핵심 하네스 파일 무결성 검증 + integrity hash + yaml-driven STEP 마커 검증.

/handoff STEP 2.8-E 에서 호출. Task 8 (AC-8, D-005) 추가:
- `load_policy(yaml_path)` — `.claude/harness-policy.yaml` 로드
- `verify_steps(project_root, policy)` — STEP 마커 + 코드 블록 검증

기존 `verify(project_root)` (CRITICAL_FILES) 는 그대로 보존 — 두 책임 분리.
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# 핵심 파일 (없으면 FAIL)
CRITICAL_FILES = [
    ".claude/settings.json",
    ".claude/memory/graph/graph_meta.yaml",
]

# 권장 파일 (없으면 WARN)
RECOMMENDED_FILES = [
    ".claude/commands/handoff.md",
    ".claude/commands/rpi.md",
]


@dataclass
class VerifyResult:
    passed: bool = True
    missing_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    integrity_hash: str = ""


def verify(project_root: str) -> VerifyResult:
    """핵심 하네스 파일 존재 확인."""
    root = Path(project_root)
    result = VerifyResult()

    for f in CRITICAL_FILES:
        if not (root / f).exists():
            result.passed = False
            result.missing_files.append(f)

    for f in RECOMMENDED_FILES:
        if not (root / f).exists():
            result.warnings.append(f"recommended file missing: {f}")

    if result.passed:
        result.integrity_hash = compute_integrity_hash(project_root)

    return result


def compute_integrity_hash(project_root: str) -> str:
    """핵심 파일들의 SHA256 결합 해시."""
    root = Path(project_root)
    hasher = hashlib.sha256()
    for f in sorted(CRITICAL_FILES + RECOMMENDED_FILES):
        path = root / f
        if path.exists():
            hasher.update(f.encode("utf-8"))
            hasher.update(path.read_bytes())
    return f"sha256:{hasher.hexdigest()}"


# ────────────────────────────────────────────────────────────
# Task 8 (AC-8, D-005): yaml-driven STEP 마커 검증
# ────────────────────────────────────────────────────────────


@dataclass
class StepPolicy:
    """One STEP entry in `.claude/harness-policy.yaml`."""
    id: str
    marker: str
    file: str
    description: str = ""


@dataclass
class Violation:
    """Marker / code-block violation detected by verify_steps()."""
    step_id: str
    severity: str  # "P0" | "P1"
    kind: str  # "missing_file" | "missing_marker" | "missing_code_block"
    file: str
    detail: str = ""


_CODE_BLOCK_AFTER_MARKER_RE = re.compile(r"```[a-zA-Z0-9_+-]*\n", re.MULTILINE)


def _segment_after_marker(text: str, marker_end: int) -> str:
    """Slice text from marker_end up to the next HARNESS marker or `## ` h2 header.

    Prevents code blocks belonging to a *later* STEP from satisfying an
    earlier STEP's requirement.
    """
    next_marker = text.find("<!-- HARNESS:", marker_end)
    next_h2 = text.find("\n## ", marker_end)
    candidates = [c for c in (next_marker, next_h2) if c >= 0]
    end = min(candidates) if candidates else len(text)
    return text[marker_end:end]


def load_policy(yaml_path: str | Path) -> list[StepPolicy]:
    """Parse the harness-policy.yaml file into a list of StepPolicy."""
    yaml_path = Path(yaml_path)
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    raw_steps = data.get("required_steps") or []
    return [StepPolicy(**s) for s in raw_steps]


def verify_steps(
    project_root: str | Path, policy: list[StepPolicy]
) -> list[Violation]:
    """Verify each STEP marker exists in its target file with a code block.

    Returns the list of violations. Empty list = all STEPs pass.
    P0 conditions: missing target file / missing marker / no code block within
    `_MARKER_LOOKAHEAD_BYTES` bytes after the marker.
    """
    project_root = Path(project_root)
    violations: list[Violation] = []

    for step in policy:
        target = project_root / step.file
        if not target.exists():
            violations.append(
                Violation(
                    step_id=step.id,
                    severity="P0",
                    kind="missing_file",
                    file=step.file,
                    detail=f"file not found at {target}",
                )
            )
            continue

        text = target.read_text(encoding="utf-8")
        marker_idx = text.find(step.marker)
        if marker_idx < 0:
            violations.append(
                Violation(
                    step_id=step.id,
                    severity="P0",
                    kind="missing_marker",
                    file=step.file,
                    detail=f"marker {step.marker!r} not found",
                )
            )
            continue

        segment = _segment_after_marker(text, marker_idx + len(step.marker))
        if not _CODE_BLOCK_AFTER_MARKER_RE.search(segment):
            violations.append(
                Violation(
                    step_id=step.id,
                    severity="P0",
                    kind="missing_code_block",
                    file=step.file,
                    detail=(
                        "no fenced code block in segment between marker "
                        "and next HARNESS marker / h2 header"
                    ),
                )
            )

    return violations
