"""Render TimelineModel as a standalone static HTML document."""
from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote


_TYPE_LABELS = {
    "decisions": ("결정한 것", "#d9f0df"),
    "decision": ("결정한 것", "#d9f0df"),
    "bugs": ("고친 버그", "#f9d9d7"),
    "bug": ("고친 버그", "#f9d9d7"),
    "learnings": ("배운 것", "#fbefc7"),
    "learning": ("배운 것", "#fbefc7"),
    "architecture": ("구조 설계", "#eadcf8"),
    "compliance-audit": ("감사", "#eceff3"),
}


def render_timeline_html(
    model: Any,
    output_path: str,
    project_root: str,
    beginner: bool = False,
    diagnosis: tuple[Any, dict] | None = None,
) -> Path:
    """Write a standalone HTML timeline and return the output path."""
    root = Path(project_root).resolve()
    out = Path(output_path).resolve()
    if os.path.commonpath([str(out), str(root)]) != str(root):
        raise ValueError(f"output_path must stay inside project_root: {output_path}")

    out.parent.mkdir(parents=True, exist_ok=True)
    html_doc = _document(model, beginner=beginner, diagnosis=diagnosis, project_root=str(root))
    out.write_text(html_doc, encoding="utf-8")
    return out


def _document(model: Any, *, beginner: bool, diagnosis: tuple[Any, dict] | None, project_root: str) -> str:
    cycles = list(getattr(model, "cycles", []))
    roadmap = getattr(model, "roadmap", None)
    coverage = getattr(model, "coverage", None)
    done = list(getattr(roadmap, "done", [])) if roadmap else []
    remaining = list(getattr(roadmap, "remaining", [])) if roadmap else []
    total = len(done) + len(remaining)
    first_date = cycles[0].date if cycles else "start"
    last_date = cycles[-1].date if cycles else "now"
    coverage_mode = getattr(coverage, "mode", "digest") if coverage else "digest"
    coverage_note = (
        "요약 수준 - 결정/발화 기록이 적습니다"
        if coverage_mode == "digest"
        else "기록 충분 - 결정/발화 기록을 함께 표시합니다"
    )
    guide = (
        "<p class=\"guide\">각 카드는 한 번의 작업 사이클입니다. 아래로 읽으면 프로젝트 흐름이 이어집니다.</p>"
        if beginner
        else ""
    )

    cycle_html = "\n".join(_cycle_card(c) for c in cycles)
    if not cycle_html:
        cycle_html = (
            "<section class=\"empty\"><h2>아직 사이클 기록이 없습니다</h2>"
            "<p>/rpi와 /handoff 한 사이클을 마치면 여기에 나타납니다.</p></section>"
        )

    roadmap_html = "\n".join(f"<li>{_e(item)}</li>" for item in remaining)
    if not roadmap_html:
        roadmap_html = "<li>남은 로드맵 항목이 없습니다.</li>"
    diagnosis_html = ""
    if diagnosis is not None:
        diagnosis_html = render_diagnosis_panel(diagnosis[0], diagnosis[1], project_root)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Timeline</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: #f7f3ec;
    color: #202225;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.65;
  }}
  main {{ max-width: 760px; margin: 0 auto; padding: 48px 20px 72px; }}
  h1 {{ font-size: 34px; margin: 0 0 8px; letter-spacing: 0; }}
  h2 {{ font-size: 20px; margin: 0 0 8px; letter-spacing: 0; }}
  h3 {{ font-size: 17px; margin: 0 0 6px; letter-spacing: 0; }}
  .meta, .coverage, .date, .source {{ color: #60646c; font-size: 14px; }}
  .coverage {{ display: inline-block; margin-top: 10px; padding: 4px 8px; border: 1px solid #d8d1c5; border-radius: 6px; }}
  .start, .now, .future, .empty {{
    border-left: 3px solid #2f6f73;
    padding: 14px 0 14px 18px;
    margin: 28px 0;
  }}
  .cycle {{
    border-left: 3px solid #bbb2a5;
    padding: 18px 0 18px 18px;
    margin: 18px 0;
  }}
  .summary {{ margin: 8px 0 10px; }}
  .chip {{
    display: inline-block;
    border-radius: 6px;
    padding: 2px 8px;
    margin: 4px 6px 4px 0;
    font-size: 13px;
    border: 1px solid rgba(0,0,0,.08);
  }}
  blockquote {{
    margin: 8px 0;
    padding: 8px 12px;
    background: #fffaf2;
    border-left: 3px solid #d6a84f;
  }}
  details {{ margin-top: 8px; }}
  ul {{ padding-left: 22px; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }}
</style>
</head>
<body>
<main>
  <header>
    <h1>Project Timeline</h1>
    <p class="meta" title="{_attr(f'{len(cycles)} cycles {first_date} to {last_date}')}">
      {len(cycles)} cycles · { _e(first_date) } → { _e(last_date) } · roadmap {len(done)}/{total}
    </p>
    <span class="coverage">{_e(coverage_mode)} · {_e(coverage_note)}</span>
    <div class="legend">
      <span class="chip" style="background:#d9f0df">결정한 것</span>
      <span class="chip" style="background:#f9d9d7">고친 버그</span>
      <span class="chip" style="background:#fbefc7">배운 것</span>
      <span class="chip" style="background:#eadcf8">구조 설계</span>
      <span class="chip" style="background:#eceff3">감사</span>
    </div>
    {guide}
  </header>
  <section class="start"><h2>START</h2><p>프로젝트 시작 - 여기서 출발합니다.</p></section>
  {cycle_html}
  <section class="now"><h2>지금 여기</h2><p>로드맵 진행률 {len(done)}/{total}</p></section>
  {diagnosis_html}
  <section class="future"><h2>남은 로드맵</h2><ul>{roadmap_html}</ul></section>
</main>
</body>
</html>"""


def render_diagnosis_panel(model: Any, narrated: dict, project_root: str) -> str:
    root = Path(project_root).resolve()
    ordered = narrated.get("ordered", getattr(model, "findings", []))
    grouped = {
        "cleanup": [f for f in ordered if f.category == "cleanup"],
        "next_action": [f for f in ordered if f.category == "next_action"],
        "efficiency": [f for f in ordered if f.category == "efficiency"],
    }
    sections = "\n".join(_diagnosis_section(name, findings, root) for name, findings in grouped.items())
    engine = _attr(narrated.get("engine", "rule"))
    narrative = _e(narrated.get("narrative", ""))
    total = _e(str(getattr(model, "counts", {}).get("total", len(ordered))))
    return f"""<section class="diagnosis" data-engine="{engine}">
  <h2>프로젝트 진단</h2>
  <p class="meta">{narrative} · total {total}</p>
  {sections}
</section>"""


def _cycle_card(cycle: Any) -> str:
    title = _e(getattr(cycle, "title", "") or f"Cycle {getattr(cycle, 'cycle_key', '')}")
    date = _e(getattr(cycle, "date", ""))
    summary = _paragraph(getattr(cycle, "summary", ""))
    next_task = _e(getattr(cycle, "next_task", ""))
    next_html = f"<blockquote>{next_task}</blockquote>" if next_task else ""
    decisions = "\n".join(_decision_chip(d) for d in getattr(cycle, "decisions", []))
    utterances = list(getattr(cycle, "utterances", []))
    utter_html = _utterance_html(utterances)
    coverage = getattr(cycle, "coverage", {}) or {}
    source_counts = coverage.get("source_counts", {})
    source = _e(f"memory {source_counts.get('memory', 0)} · utterances {source_counts.get('utterances', 0)}")
    return f"""<article class="cycle">
  <p class="date">{date}</p>
  <h2>{title}</h2>
  <div class="summary">{summary}</div>
  {decisions}
  {utter_html}
  {next_html}
  <p class="source">{source}</p>
</article>"""


def _diagnosis_section(name: str, findings: list[Any], root: Path) -> str:
    labels = {"cleanup": "청소거리", "next_action": "다음 할 일", "efficiency": "운영 효율"}
    rows = "\n".join(_finding_row(f, root) for f in findings)
    if not rows:
        rows = "<p class=\"meta\">신호 없음</p>"
    return f"<div class=\"diag-group\"><h3>{_e(labels.get(name, name))}</h3>{rows}</div>"


def _finding_row(finding: Any, root: Path) -> str:
    title = _e(finding.title)
    detail = _e(finding.detail)
    suggestion = _e(finding.suggestion)
    severity = _e(finding.severity)
    confidence = _e(finding.confidence)
    evidence = _evidence_html(finding.evidence_ref, root)
    attr = _attr(f"{finding.rule_id}:{finding.confidence}")
    return f"""<article class="diag-finding" title="{attr}">
  <span class="chip severity-{severity}">{severity}</span>
  <span class="chip">{confidence}</span>
  <h3>{title}</h3>
  <p>{detail}</p>
  <p><strong>제안:</strong> {suggestion}</p>
  <p class="source">근거: {evidence}</p>
</article>"""


def _evidence_html(evidence_ref: str, root: Path) -> str:
    ref = str(evidence_ref)
    if re_match_short_sha(ref):
        return f"<code>{_e(ref)}</code>"
    if "://" in ref or Path(ref).is_absolute():
        raise ValueError(f"evidence_ref must be repo-relative: {ref}")
    target = (root / ref).resolve()
    if os.path.commonpath([str(target), str(root)]) != str(root):
        raise ValueError(f"evidence_ref must stay inside project_root: {ref}")
    href = quote(ref.replace("\\", "/"))
    return f'<a href="{_attr(href)}">{_e(ref)}</a>'


def re_match_short_sha(value: str) -> bool:
    return len(value) in {7, 8, 9, 10, 11, 12} and all(c in "0123456789abcdefABCDEF" for c in value)


def _decision_chip(node: dict) -> str:
    kind = str(node.get("type", "decision"))
    label, color = _TYPE_LABELS.get(kind, ("기록", "#eceff3"))
    title = _e(str(node.get("title", "")))
    attr = _attr(str(node.get("source", "")))
    return f'<span class="chip" style="background:{color}" title="{attr}">{_e(label)} · {title}</span>'


def _utterance_html(utterances: list[Any]) -> str:
    if not utterances:
        return ""
    first = utterances[:2]
    lines = []
    for utt in first:
        category = _e(getattr(utt, "category", "utterance"))
        text = _e(getattr(utt, "text", ""))
        ts = _attr(getattr(utt, "ts", ""))
        lines.append(f'<blockquote title="{ts}"><strong>{category}</strong>: {text}</blockquote>')
    if len(utterances) > 2:
        hidden = "".join(
            f"<p>{_e(getattr(utt, 'text', ''))}</p>"
            for utt in utterances[2:]
        )
        lines.append(f"<details><summary>더 보기</summary>{hidden}</details>")
    return "\n".join(lines)


def _paragraph(text: str) -> str:
    escaped = _e(str(text))
    if not escaped:
        return "<p>요약 없음</p>"
    return "".join(f"<p>{part}</p>" for part in escaped.split("\n") if part.strip())


def _e(value: str) -> str:
    return html.escape(str(value), quote=True)


def _attr(value: str) -> str:
    return html.escape(str(value), quote=True)
