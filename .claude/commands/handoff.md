# /handoff — 세션 종료 & 다음 세션 인계

## user_level 감지 (톤 조절)

CLAUDE.md의 frontmatter에서 `user_level` 값을 확인하세요.

- `user_level: beginner` → 모든 출력을 쉬운 말로:
  - "세션 종료" → "오늘 작업 마무리"
  - "인계" → "다음에 이어서 할 수 있게 정리"
  - context.md 중단 지점: "오늘 한 일: {쉬운 설명}" / "다음에 할 일: {쉬운 설명}"
  - 컴플라이언스 감사 결과: "보안 검사 결과: 문제없음 ✅" / "확인이 필요한 부분이 있어요 ⚠️"
- `user_level: intermediate` → 전문 용어 + 괄호 설명
- `user_level: advanced` 또는 미설정 → 기존 동작 그대로

**이후 모든 STEP의 출력 텍스트에 이 톤을 적용하세요.**

---

> 사용법: `/handoff`
> 타이밍: 작업을 마치거나 중간에 끊어야 할 때

---

## ━━━ STEP 1: 현재 세션 작업 파악 ━━━

다음 파일들을 읽고 오늘 세션에서 무슨 일이 있었는지 파악하세요:

1. `docs/checklist.md` — 오늘 체크된 항목과 미완료 항목
2. `docs/context.md` — 현재 기록된 상태
3. 이번 대화에서 실제로 수정/생성된 파일 목록 (대화 기록 기반)

---

## ━━━ STEP 2: docs 파일 업데이트 ━━━

### docs/checklist.md 업데이트
이번 세션에서 완료된 항목을 `[x]`로 체크하세요.
새로 발견된 태스크가 있다면 적절한 Phase에 추가하세요.

### docs/context.md 업데이트
파일 맨 위에 아래 블록을 추가하세요 (기존 내용은 아래로 밀기):

```markdown
## 🔖 중단 지점 — [날짜 YYYY-MM-DD]

### 오늘 완료한 것
- [완료 항목 1]
- [완료 항목 2]

### 미완료 / 중단된 것
- [미완료 항목] — 이유: [왜 멈췄는지]

### ⚡ 다음 세션 첫 번째 Task
> [다음에 가장 먼저 해야 할 것을 한 문장으로]

### 주의사항 (다음 세션에서 알아야 할 것)
- [특이사항, 임시 해결책, 건드리면 안 되는 것 등]
```

#### Hot tier 압축 규칙 (context.md)
- 세션당 중단 지점 블록 **최대 20줄**
- 코드 스니펫 금지 — 파일 경로만 기재
- 근거(Why) 금지 — `decisions/` 메모리로 분리
- 단문 불릿 포인트만 사용
- 중복 주의사항은 최신 것만 유지

---

## ━━━ STEP 2.5: 메모리 관리 (ASMR 3-Tier) ━━━

> ⚠️ `.claude/memory/` 폴더가 **없으면** 이 단계를 건너뛰세요.
> 첫 번째 handoff에서 폴더가 없으면 "메모리 시스템을 활성화하시겠습니까?" 라고 사용자에게 확인하세요.

이번 세션의 작업 내용을 분석하여 장기 메모리를 관리합니다.

### 2.5-B. 3단계 기억 관계 분석

이번 세션에서 발생한 **주요 변경사항 각각**에 대해 다음을 판단하세요:

**Update (갱신)**: 기존 메모리의 내용이 변경/무효화된 경우
→ 해당 메모리 파일을 수정하고 `event_date` 갱신, 또는 `status: superseded`로 변경

**Extend (확장)**: 기존 메모리에 새로운 디테일이 추가된 경우
→ 해당 메모리 파일에 내용을 병합 (새 섹션 추가 또는 기존 섹션 보강)

**Derive (파생)**: 여러 정보를 종합하여 새로운 지식이 도출된 경우
→ 새 메모리 파일 생성 (적절한 카테고리 폴더에), `references`에 원본 ID 기록

### 2.5-B-2. 반복 실수 로그 체크 (복리 학습)

이번 세션에서 **버그 / 테스트 실패 / 린트 실패 / Verification Gate 실패** 가 1회 이상 발생했는가?

- **예** → `.claude/memory/learnings/recurring-mistakes.md` 를 열어 아래 표에 1행 이상 추가:
  ```markdown
  | 날짜 | 도메인 | 실수 | 원인 | 재발 방지책 |
  |------|--------|------|------|-------------|
  | YYYY-MM-DD | [도메인] | [무엇을 잘못했나] | [왜 발생했나] | [다음엔 어떻게] |
  ```
  파일이 없으면 헤더와 함께 신규 생성하세요.
- **아니오** → 스킵.

> 이 로그는 보리스의 "복리 학습" 원칙 — 같은 실수를 반복하지 않기 위한 단일 진실 소스입니다.
> 갱신 누락 시 STEP 3 인계 보고에 🟡 경고로 표시합니다.

### 2.5-C. 메모리 생성 판단 기준

아래 질문 중 하나라도 "예"일 때만 메모리를 생성/수정하세요:

1. "이 정보가 다음 세션 이후에도 필요한가?"
2. "이 결정을 나중에 왜 그랬는지 물을 수 있는가?" → `decisions/`
3. "시스템 구조나 데이터 흐름이 바뀌었는가?" → `architecture/`
4. "버그를 고쳤고, 같은 유형의 버그가 재발할 수 있는가?" → `bugs/`
5. "외부 도구/API에 대해 새로 알게 된 것이 있는가?" → `learnings/`

**만들지 않는 것**: 오타 수정, import 정리, 단순 리팩토링, 주석 추가

### 2.5-D. _index.md 업데이트 (참조 추적 포함)

메모리 생성/수정/삭제가 발생했으면 `.claude/memory/_index.md`를 반드시 업데이트하세요:
- "최근 세션" 테이블에 이번 세션 추가
- "카테고리별 목록"에 새 메모리 추가 또는 기존 항목 상태 변경
- "도메인별 태그 색인"에 태그 추가/수정
- Warm/Cold 카운트 헤더 갱신

**참조 추적 테이블 갱신:**
- 이번 세션에서 `/rpi`가 Read한 메모리 → `마지막 참조 세션` = 현재 세션 번호
- Update/Extend/Derive 대상이 된 메모리도 참조로 간주
- 위에 해당하지 않는 메모리 → `비활성 세션 수` += 1

### 2.5-E. docs/context.md 경량화

`docs/context.md`는 **최근 3세션분의 중단 지점 정보만 유지**하세요.
3세션 이전의 기록은 mempalace 가 담당하므로 삭제합니다.

context.md 상단에 티어 현황 헤더를 유지하세요:
```markdown
# 맥락 (Hot Memory)
## 현재 Phase: [Phase X]
> 활성 도메인: [domain1, domain2]
> Warm: [N]개 | Cold: [M]개
```

### 2.5-F. 티어 강등 판단 (Warm → Cold)

> ⚠️ `archive/` 폴더가 **없으면** 이 단계를 건너뛰세요.
> archive 폴더가 없고 강등 대상이 존재하면: "archive/ 폴더가 없습니다. 3-tier를 활성화하시겠습니까?" 라고 확인하세요.

`_index.md`의 참조 추적 테이블을 분석하여 강등 대상을 식별합니다.

**강등 조건 (하나라도 해당 시):**
1. `status: superseded` → 즉시 `archive/{category}/`로 이동
2. `비활성 세션 수` >= 10 → `status: archived`로 변경 후 `archive/{category}/`로 이동
3. Warm active 메모리 > 50개 → 비활성 세션 수가 가장 높은 것부터 강등 (40개 이하까지)

**강등 수행 절차:**
1. 대상 파일의 `status`를 `archived`, `tier`를 `cold`로 변경
2. 파일을 `.claude/memory/archive/{category}/`로 이동
3. `_index.md`에서 해당 항목 제거 + 참조 추적 테이블에서 삭제
4. `_archive_index.md`에 해당 항목 추가
5. 강등된 메모리 목록을 STEP 3 인계 보고에 포함

> 강등은 물리적 이동이다 — 파일이 두 곳에 동시 존재하면 안 된다.

### 2.5-H. Cold 승격 확정

이번 세션의 `/rpi`에서 Cold tier에서 읽어온 메모리가 있고,
실제로 해당 메모리가 작업에 활용되었다면:

1. 해당 파일을 `archive/{category}/` → `memory/{category}/`로 이동
2. frontmatter 갱신: `status: active`, `tier: warm`, `reactivated_from: archived`, `reactivated_session: {N}`
3. `_index.md`에 추가 + 참조 추적 테이블에 등록 (마지막 참조 세션 = 현재)
4. `_archive_index.md`에서 제거

---

## ━━━ STEP 2.5.5: Dispatcher Carry-Forward ━━━

> ⚠️ `.atomy/dispatcher-state.yaml` 부재 시 자동으로 `dispatcher_status: none` 처리됨.
> dispatcher 는 carry-forward 를 읽기/기록만 — FSM 전이를 강제하지 않는다.

이번 세션에 in-flight WorkOrder(`/implement` 로 Codex 에 위임한 작업)가 있으면 그
상태를 `docs/context.md` 최신 중단점 블록에 박아 다음 세션 `/rpi` 가 잇게 한다.

```python
from pathlib import Path
from atomy_toolkit.dispatcher import load_carryforward

cf = load_carryforward(Path(".atomy/dispatcher-state.yaml"))
# cf.block 을 docs/context.md 최상단(최신) "## 🔖 중단 지점" 블록 안의
# "### Dispatcher Carry-Forward" 로 splice (없으면 새로 추가).
print(f"dispatcher carry-forward: status={cf.priority} state={cf.state}")
```

- `cf.has_work and cf.priority == "preempt"` (blocked/failed) → 인계 보고(STEP 3)에
  **🔧 In-Flight WorkOrder (preempt)** 로 표기 + `cf.recommended_action` 명시.
- `cf.priority == "informational"` (executing/verifying/...) → 정보성 표기.
- `cf.warning` 비어있지 않으면(state 파일 corrupt) WARN 표기 후 진행(비블록).

---

## ━━━ STEP 2.5.6: Plan Bookkeeping Reconcile ━━━

> ⚠️ `docs/plans/` 부재 시 스킵. reconcile 은 box 를 flip 하지 않는다 — 안전 범위
> (dispatcher-known slug ∪ 마커 보유 plan)에서만 `**Status:** shipped` 봉인 / 그 외 경고.

이번 세션이 끝낸 plan 의 완료 마감이 누락됐는지 점검하고 안전 범위에서 봉인한다.

```python
from atomy_toolkit.dispatcher.reconcile import reconcile_plan_bookkeeping
rep = reconcile_plan_bookkeeping("docs/plans", ".atomy/dispatcher-state.yaml")
print(f"reconcile: sealed={len(rep.auto_sealed)} warn={len(rep.warnings)}")
for name in rep.auto_sealed:
    print(f"  🔒 sealed: {name}")
for name, why in rep.warnings:
    print(f"  ⚠️ {name}: {why}")
```

- `auto_sealed`/`warnings` 가 비어있지 않으면 STEP 3 인계 보고의 **🧮 Plan Reconcile** 라인에 표기.

---

## ━━━ STEP 2.6: Compliance Audit (조직 / 스타터킷 / 프레임워크 프로젝트) ━━━

> ⚠️ 활성화 조건: 프로젝트의 `CLAUDE.md` 에 다음 중 하나가 박혀있을 때 실행:
>
> | 플래그 | 의미 | 동작 |
> |---|---|---|
> | `compliance: required` | 일반 조직 프로젝트 (단일 프로젝트 scope) | 표준 audit (2.6-A ~ 2.6-D) |
> | `compliance: cascade-aware` | starter kit / framework / library — 본 프로젝트의 변경이 *다른 다수 프로젝트* 에 cascade 됨 | 표준 audit + **cascade impact 분석** (compliance-reviewer agent 의 input 에 "이 변경의 cascade 범위: `.claude/` 하위, `_global-toolkit/core/*.yaml`, `templates/`, `installers/` 등이 신규 또는 기존 사용자 프로젝트에 영향. 위반 시 *모든 cascade 사용자* 에게 전파됨" context 첨부) |
> | (둘 다 부재) | 개인 프로젝트 | "개인 프로젝트 — 감사 스킵" 표시 후 STEP 3 진행 |
>
> **본인이 cascade-aware 판정 시 (자동 승격):** CLAUDE.md 에 명시적 박음 안 했더라도 (1) `.claude/skills/`, `.claude/commands/`, `.claude/agents/` 등 *core toolkit asset* 수정, OR (2) `_global-toolkit/core/*.yaml` 수정, OR (3) `templates/` 또는 `installers/` 수정 시 cascade-aware 로 자동 승격하여 audit 실행. audit 로그에 "cascade-aware auto-promoted (사유: <수정된 cascade source>)" 명시. 본 override 가 sub-task L spike audit §5-C 의 starter kit 예외 케이스 해소 (handoff workflow 의 false negative 차단).

### 2.6-A.0 transport 사전 감사 + authority lookup

<!-- HARNESS:STEP-2.6 -->

Full work-order audit path: first call `run_handoff_audit_work_order()`, which performs MCP `tools/list` capability discovery for `get_handoff_audit_capabilities` and `run_handoff_audit_work_order`, sends the redacted work order to compliance-service when both tools are present, sanitizes the returned `audit_result`, and normalizes missing/timeout/malformed responses to `work_order_result.transport=fallback` so handoff can continue. If the full work-order path is unavailable, keep the existing `query_authorities()` fallback path and pass both `work_order_result` and `authority_result` into the audit narrative.

`atomy_toolkit.compliance.transport.audit()` 가 기존 pre-audit 를 수행하고, `query_authorities()` 가 compliance-service MCP 의 `lookup_authorities_for_handoff` 를 우선 호출해 issue-aware 법령/판례/가이던스를 조회합니다. 해당 tool 이 없거나 실패하면 legacy read-only chain (`list_categories` → `search_rules_in_category` → `fetch_rule_body` → `fetch_reference_body`) 으로 fallback 합니다. MCP endpoint 가 없거나 실패하면 `authority_result.transport=fallback` 으로 정규화하고 handoff 는 계속 진행합니다.

```python
from pathlib import Path

from atomy_toolkit.compliance.audit_v2 import AuditPrompt
from atomy_toolkit.compliance.work_order import (
    build_handoff_audit_work_order,
    render_work_order_prompt_pack,
    sanitize_audit_result,
)
from atomy_toolkit.compliance.transport import (
    audit,
    query_authorities,
    run_handoff_audit_work_order,
)

# 이번 세션 diff (수정 파일 목록 + 실행 Bash 명령) 를 단일 문자열로 직렬화한 후 전달
session_diff = "<this session's serialized diff>"
session_id = "<stable session id or timestamp>"
session_memory_ref = f"memtemple-session:{session_id}"
work_order = build_handoff_audit_work_order(
    session_id=session_id,
    project_root=Path.cwd(),
    asmr_summary={"summary": "<ASMR pass 1 summary>"},
    session_log_path=Path("<session jsonl path>") if "<session jsonl path>" else None,
    session_memory_ref=session_memory_ref,
    changed_files=["<repo-relative changed file>"],
    command_log=[{"command": "<redacted command summary>"}],
    tool_call_log=[{"tool": "<redacted tool summary>"}],
    memtemple_wing="<wing>",
    max_prompts=6,
)
prompt_pack = render_work_order_prompt_pack(work_order)
work_order_result = run_handoff_audit_work_order(
    work_order,
    mode="auto",
    max_parallel=4,
    timeout_seconds=45,
)
authority_result = query_authorities(
    AuditPrompt(
        topic_id="handoff-session",
        title="Session compliance authority lookup",
        scope={
            "session_diff": session_diff[:4000],
            "work_order": {
                "issue_manifest": work_order["issue_manifest"],
                "source_inventory": work_order["source_inventory"],
                "issue_overflow": work_order["issue_overflow"],
            },
        },
        question=(
            "Find applicable laws, precedents, and guidance for this "
            "handoff compliance review using the issue-aware work order."
        ),
        expected_authorities=["law", "precedent", "guidance"],
    ),
    timeout_seconds=45,
)
result = audit(session_diff, transport="auto")
print(
    f"compliance pre-audit: transport={result['transport']} "
    f"status={result['status']} violations={len(result['violations'])}"
)
print(
    f"work-order audit: transport={work_order_result['transport']} "
    f"status={work_order_result['status']} "
    f"verdict={(work_order_result.get('audit_result') or {}).get('verdict', 'n/a')}"
)
print(
    f"authority lookup: transport={authority_result['transport']} "
    f"status={authority_result['status']} "
    f"authorities={len(authority_result['authorities'])}"
)
coverage = authority_result.get("coverage") or {}
issue_results = authority_result.get("issue_results") or []
print(
    f"authority coverage: status={coverage.get('status', 'n/a')} "
    f"issue_extraction={coverage.get('issue_extraction_status', 'n/a')} "
    f"issues={len(issue_results)}"
)
# result, work_order_result, authority_result, work_order, prompt_pack 를 compliance-reviewer agent 의 추가 입력으로 첨부
```

violations 가 있으면 2.6-A 의 자연어 분석에 우선순위로 포함하고, `work_order.prompts` 는 compliance-reviewer 의 병렬 audit prompt pack 으로 사용합니다. `authority_result.authorities` 가 있으면 authority summary / finding 근거에 함께 인용합니다. `authority_result.coverage` 와 `authority_result.issue_results` 가 있으면 issue 별 coverage.status / engine_used / timeout warning 을 감사 입력에 함께 포함합니다. 둘 다 비어 있으면 work_order 기반 자연어 분석만 사용합니다.

### 2.6-A. 감사 에이전트 호출

`compliance-reviewer` 서브에이전트(`.claude/agents/compliance-reviewer.md`)를 호출하여 다음을 전달하세요:
- 이번 세션에서 수정·생성된 파일 목록
- 이번 세션에서 실행한 Bash 명령 목록 (특히 파괴적·네트워크 명령)
- 신규 의존성 diff
- **2.6-A.0 의 `result` (transport / status / violations)** — MCP 풀 사전 결과
- 프로젝트 `.claude/compliance/policy.md` (없으면 `~/.claude/compliance/policy.md`)
- 프로젝트 `.claude/compliance/checklist.md` (없으면 전역)

### 2.6-B. 감사 로그 저장

에이전트 결과를 `.claude/memory/compliance-audit/SESSION-{N}.md` 에 저장 (폴더 없으면 생성).
판정(PASS / WARN / FAIL) 과 위반 항목 상세를 포함합니다.

### 2.6-C. FAIL 시 처리

- 판정이 **🔴 FAIL** 이면 STEP 3 정상 인계 보고를 출력하지 않고 다음 메시지를 출력:
  ```
  🚨 Compliance Audit FAILED — 세션 종료 보류
  위반 항목:
    • [항목 + 파일:라인 + 권고]
  조치 후 /handoff 를 다시 실행하거나, 명시적 예외 승인이 필요하면
  CLAUDE.md 에 `compliance-override: [사유]` 를 추가하고 재실행하세요.
  ```
- **🟡 WARN** / **🟢 PASS** 면 STEP 3 인계 보고의 "⚖️ Compliance" 섹션에 결과를 포함하고 정상 진행합니다.

---

## ━━━ STEP 2.7: memtemple save — 현재 세션 대화를 vault sessions/ 에 박음 ━━━

<!-- HARNESS:STEP-2.7 -->

> **2026-05-20 변경**: 종전 `mempalace mine` 2-leg → **memtemple save 단일 leg** 로 치환.
> mempalace 의존 제거 (`atomy_toolkit.memtemple.core.session_locator` 가 self-contained).
> 실패해도 /handoff 자체는 블록하지 않는다 (경고만).

**동작:**
- 현재 환경의 가장 최근 세션 JSONL 을 자동 탐색 (`find_session_log()` 가 Claude Code / Gemini path 지원)
- 발견 시 vault wing 의 `sessions/` room 에 turn-pair markdown drawer 가 박힘 + curation subagent 가 frontmatter 보강

**권장 호출 방식 — MCP tool (Zero-Allowance 정합):**

`atomy-toolkit-mcp` MCP server 의 `memtemple_save_tool` 을 직접 호출. 인자 없이 호출 시 도구가 자동으로 `find_session_log()` 호출하여 세션 로그 위치 추론.

- 인자 부재 → 자동 추론 (Claude Code `~/.claude/projects/` 또는 Gemini `~/.gemini/tmp/`)
- 인자 명시 → `session_log=<path>, wing=<wing_name>` 전달
- 도구 내부에서 `--plugin claude_code` 기본 적용 (Click 옵션 default)

결과 처리:
- 성공: `~/.memtemple/<wing>/sessions/<thread>__<source_type>.md` 에 drawer 박힘. frontmatter 의 `source_type` 자동 인식 (Claude Code = `claude_code`, Codex = `codex`, Antigravity = `antigravity`)
- WARN: 세션 로그 미발견 (Codex 같은 미지원 path) — `session_log=<path>` 명시 호출 권장
- FAIL: 세션 로그는 disk 보존, 재시도 가능

**Fallback reference (MCP tool 미등록 환경 외, LLM 자체 shell 호출 차단):**

```text
# PowerShell (Windows):
$env:PYTHONIOENCODING = "utf-8"   # cp949 em-dash 회피

# 1) atomy-toolkit CLI 가 PATH 에 없으면 skip
if (-not (Get-Command atomy-toolkit -ErrorAction SilentlyContinue)) {
    Write-Host "memtemple save: skip — atomy-toolkit not on PATH"
    return
}

# 2) 자동 추론 호출 — --source 미제공 시 find_session_log() 내부 호출 (M.1 SHIP, 2026-05-22)
& atomy-toolkit memtemple save --plugin claude_code
if ($LASTEXITCODE -eq 0) {
    Write-Host "memtemple save: OK — sessions/ drawer 박힘"
} else {
    Write-Host "memtemple save: WARN/FAIL — exit $LASTEXITCODE (session preserved on disk, retry possible)"
}
```

```text
# Bash (POSIX):
export PYTHONIOENCODING=utf-8

if ! command -v atomy-toolkit >/dev/null 2>&1; then
    echo "memtemple save: skip — atomy-toolkit not on PATH"
else
    # 자동 추론 호출 — --source 미제공 시 find_session_log() 내부 호출
    if atomy-toolkit memtemple save --plugin claude_code; then
        echo "memtemple save: OK — sessions/ drawer 박힘"
    else
        echo "memtemple save: WARN/FAIL — non-zero exit (session preserved on disk)"
    fi
fi
```

**인계 보고에 포함:**
- memtemple save 결과 (OK/WARN/skip/FAIL + 세션 JSONL 경로)
- vault sessions/ drawer 갯수 변화 (선택, `atomy-toolkit memtemple status` 출력)

> 주의: T-v1.x-A.5 (2026-05-20) 완료 — `mempalace_client.py` 는 memtemple-backed shim 으로 슬림화됨 (437→130 LOC). `MemorySnippet` schema 유지로 rerank/router/graph_client/palace_librarian 호환. mine() 은 삭제.

---

## ━━━ STEP 2.8: Harness 무결성 검증 ━━━

Knowledge Fabric 하네스 파일의 무결성을 검증한다. graph_meta.yaml 이 존재하는 프로젝트에서만 실행.

**실행:**

```python
import sys; sys.path.insert(0, '.claude/lib')
from pathlib import Path

if Path('.claude/memory/graph/graph_meta.yaml').exists():
    import harness_verifier
    result = harness_verifier.verify('.')
    if result.passed:
        print(f"Harness OK — integrity: {result.integrity_hash[:20]}...")
    else:
        print(f"Harness FAIL — missing: {', '.join(result.missing_files)}")
    if result.warnings:
        for w in result.warnings:
            print(f"  WARN: {w}")
else:
    print("Harness: skipped (Knowledge Fabric not initialized)")
```

**인계 보고에 포함:**
- Harness 검증 결과 (PASS/FAIL)
- Integrity hash (변조 감지용)
- 경고 사항

---

## STEP 2.9: Cascade Sync
프로젝트의 cascade 버전과 설치된 toolkit master cascade 버전을 비교합니다. master가 더 새 버전이면 다음 세션이 낡은 workflow/skill 자산으로 시작하지 않도록 동기화를 시도합니다.

**실행:**

```python
import sys
from pathlib import Path

try:
    from atomy_toolkit.update.cascade.sync import sync_project_cascade

    install_prefix = Path(sys.prefix)
    result = sync_project_cascade(Path("."), install_prefix=install_prefix)
    if result.updated:
        print(f"Cascade updated: project v{result.from_version} to v{result.to_version}")
    elif result.skip_reason == "master_uncommitted":
        print("Cascade master update in progress - sync deferred to next /handoff")
    elif result.skip_reason:
        print(f"Cascade sync skipped: {result.skip_reason}")
    else:
        print(f"Cascade OK (v{result.to_version or 'unknown'})")
except ImportError:
    print("Cascade sync: skipped (atomy_toolkit.update not installed yet)")
```

**인계 보고에 포함:**
- Cascade sync 결과 (updated / skipped / OK)
- 변경 시 from -> to version

---

## ━━━ STEP 3: 인계 보고 출력 ━━━

업데이트 완료 후 아래 형식으로 출력하세요:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 세션 종료 — 인계 보고
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 오늘 완료
  • [완료 항목들]

⏸️  중단 지점
  • [중단된 작업과 이유]

⚡ 다음 세션 첫 Task
  "[다음에 해야 할 것]"

📦 메모리 변경
  • 생성: [새 메모리 파일 목록]
  • 수정: [Update/Extend된 메모리]
  • 🔽 강등 (Warm→Cold): [강등된 메모리 ID와 이유]
  • 🔼 승격 (Cold→Warm): [승격된 메모리 ID]
  • (memory 폴더 미사용 시 "메모리 시스템 비활성" 표시)

📊 티어 현황
  • Hot: context.md ([N] KB)
  • Warm: [N]개 active
  • Cold: [N]개 archived

⚖️  Compliance (조직 프로젝트 시)
  • 판정: 🟢 PASS | 🟡 WARN | 🔴 FAIL (또는 "개인 프로젝트 — 스킵")
  • 감사 로그: .claude/memory/compliance-audit/SESSION-{N}.md

🧠 복리 학습
  • recurring-mistakes.md 갱신: [N행 추가 | 해당 없음 | ⚠️ 오류 발생했으나 미갱신]

🧮 Plan Reconcile
  • 봉인: [auto_sealed plan 목록 | 없음] · 경고: [warnings | 없음]

⚠️  주의사항
  • [있는 경우만]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 다음 세션 시작 문구:

  /rpi 이전 작업 이어서

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docs 업데이트 완료. 이제 /clear 하세요.
```

---

## ⚠️ 주의사항
- docs 파일 업데이트를 **먼저** 완료한 뒤 보고를 출력하세요
- "다음 세션 첫 Task"는 반드시 **행동 가능한 구체적인 한 문장**으로 작성하세요
  - ❌ "마이그레이션 계속"
  - ✅ "scanner.py를 src/data_fetcher/로 복사하고 import 경로 수정"
- 이번 세션에서 아무것도 안 했더라도 현재 상태를 그대로 기록하세요
- STEP 2.5는 `.claude/memory/` 폴더가 존재할 때만 실행하세요
- STEP 2.5-F는 `archive/` 폴더가 존재할 때만 실행하세요

---

## Compliance Audit v2 Contract Overlay

This section supersedes the legacy STEP 2.6-C hard stop behavior.

Required closure order:

1. STEP 2.5: Continuity memory pass 1.
2. STEP 2.6: memtemple save.
3. STEP 2.7: Compliance Audit v2.
4. STEP 2.8: Compliance memory pass 2.
5. STEP 3: Always print the handoff report.

FAIL/CRITICAL 이 있어도 STEP 3 handoff report 를 출력한다. Do not suppress the normal closure report. Instead, set the report status explicitly:

```yaml
closure_status: compliance_blocked
compliance_audit:
  result: FAIL | CRITICAL
  unresolved_findings: true
```

When Compliance Audit v2 reports FAIL or CRITICAL, STEP 3 must include the audit log path, a short Unresolved Findings summary, and the next concrete remediation task before `/clear`.
