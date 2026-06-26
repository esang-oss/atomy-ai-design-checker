# RPI 워크플로

## Step 0: user_level 감지 (톤 조절)

CLAUDE.md의 frontmatter에서 `user_level` 값을 확인하세요.

- `user_level: beginner` → 모든 출력을 쉬운 말로 전환:
  - "Phase" → "단계", "도메인" → "작업 영역", "메모리 티어" → 생략
  - Research 결과: "📍 지금 단계: {쉬운 설명}"
  - Plan: "이번에 할 일을 정리했어요" + 번호 목록
  - 질문: 선택지(A/B/C) 포맷 필수
- `user_level: intermediate` → 전문 용어 + 괄호 설명:
  - "현재 Phase(단계): Phase B — 데이터 모델"
- `user_level: advanced` 또는 미설정 → 기존 동작 그대로

**이후 모든 Step의 출력 텍스트에 이 톤을 적용하세요.**

---

당신은 체계적인 개발자입니다. 아래 3단계를 반드시 순서대로 수행하세요.

단, `/rpi` 는 사용자 입력과 `docs/plan.md` 를 비교하여 **네 모드 중 하나로 자동 분기**합니다. Step 1 Reader 단계에서 모드를 판정하고, Step 2 는 모드별 다른 플로우를 따릅니다.

## Mode 라우팅 테이블

Reader 는 다음을 **위에서 아래 순서로 평가**하여 첫 번째 일치하는 모드를 선택합니다:

| # | 조건 | 모드 | 질문 프레이밍 | 산출물 |
|---|------|------|---------------|--------|
| 1 | `$ARGUMENTS` 비어있음 (`/rpi` 만 호출) | **Align** | "원래 다음은 {a} 입니다. 다른 원하시는 거 있나요?" | 응답에 따라 재분기 |
| 2 | 입력이 `docs/plan.md` 다음 checklist 항목과 일치 | **Align** | "원래 계획대로 {a} 진행합니다. 맞죠?" | 승인 시 Plan 으로 |
| 3 | 명확한 버그·오타·린트·사소한 리팩토링 (≤3 파일, scope 명확) | **Trivial** | 확인 없이 Research 요약만 출력 | 기존 경량 Plan (변경 없음) |
| 4 | 입력이 계획과 불일치 | **Brainstorm** | "원래 계획은 {a} 인데 {b} 를 말씀하셨네요." | spec → plan → implement |
| 5 | 신규 기능 & 관련 spec 없음 | **Brainstorm** | "신규 기능이네요. 먼저 정리해볼게요." | spec → plan → implement |
| 6 | 신규 기능 & 관련 spec **있음** | **Plan** | "`{spec-path}` 스펙 읽었습니다. 작업으로 분해할게요." | plan 문서만 신규 생성 |

**판정 우선순위:** 1번부터 차례로 체크. 1번 조건 참이면 바로 Align, 아니면 2번 체크, 이런 식으로 진행.

**spec glob 검색 패턴** (조건 5/6 판정용):
- 새 형식: `docs/specs/*-<topic-keyword>*.md` (예: `2026-04-23-*.md`)
- 레거시: `docs/specs/<기능명>.md` (날짜 없음 — 기존 프로젝트 호환)

**skip 지원:** Brainstorm 모드 중 사용자가 `skip brainstorm` / `건너뛰어` 입력 시 → 현재까지 질문-응답을 간략 spec 으로 요약 후 Plan 모드로 전환.

**승인 게이트:**

| 모드 | 승인 게이트 | 건너뛸 수 있나? |
|------|-------------|----------------|
| Align | "그대로 진행" 응답 1회 | 예, 응답이 다른 mode 로 재분기 |
| Trivial | **없음** (바로 Step 2-3 실행) | — |
| Plan | 생성된 plan 문서에 대한 "OK" 1회 | 예, `skip plan review` 입력 시 |
| Brainstorm | 질문마다 1회 + spec 승인 1회 + plan 승인 1회 | 아니오 (skip 플래그 사용 시만 예외) |

---

## Step 1: Research (조사) — ASMR 검색 (3-Tier 라우팅)

세 가지 역할을 순서대로 수행하여 현재 작업에 필요한 맥락을 수집하세요.

### 1-A. Reader (의도 파악 + 모드 판정)

사용자 요청 "$ARGUMENTS"를 분석하여 다음을 판별하세요:
- **작업 도메인**: 어떤 도메인(폴더)에 속하는 작업인가?
- **작업 유형**: 신규 기능 / 버그 수정 / 리팩토링 / 문서화 중 무엇인가?
- **필요한 맥락 유형**: decisions / architecture / bugs / learnings 중 어떤 것이 관련될 가능성이 높은가?
- **시간 범위**: 현재 Phase 작업인가, 과거 Phase 참조가 필요한가?
- **모드 판정**: 본 파일 상단 "Mode 라우팅 테이블" 을 위에서부터 평가하여 첫 일치 모드를 선택

#### 모드 판정 세부 로직

1. **Align 모드** (`$ARGUMENTS` 비어있음 / plan 다음 Task 와 일치):
   - `docs/plan.md` 파싱 → 첫 미완료 `- [ ]` Task 를 "다음 작업 {a}" 로 추출
   - `docs/plan.md` 부재 시 → "plan.md 가 없네요. 이번 요청 내용 알려주세요." 출력하고 중단 (사용자 재입력 대기)

2. **Trivial 모드** (버그·오타·린트·사소한 리팩토링):
   - 판정 기준: 작업 유형이 "버그 수정" OR "리팩토링" AND 입력에서 수정 대상 파일 수 ≤3 추정 AND scope 명확(예: 특정 함수·파일 언급)
   - 예시: "`src/parser.py` 의 trailing whitespace 제거", "`calculate_total()` 의 변수명 오타 수정"

3. **Brainstorm 모드** (계획 불일치 / 신규 기능 & spec 없음):
   - spec 존재 여부 체크 — glob 검색:
     - 새 형식: `docs/specs/*<topic-keyword>*.md`
     - 레거시: `docs/specs/<기능명>.md`
   - topic-keyword 는 `$ARGUMENTS` 의 명사구에서 추출

4. **Plan 모드** (신규 기능 & spec 있음):
   - spec 경로를 확정하여 Research 결과에 표시

### 1-A-보조. Reader 출력 직후 체크 (신규 기능 & spec 없음)

<!-- HARNESS:STEP-RPI-1A -->

superpowers plugin 가용 여부를 사전 감지하여, 후속 Brainstorm/Plan 단계가 위임될지 toolkit fallback 으로 동작할지 한 번에 판정. (Phase 1 Task 5 의 Hybrid wiring + Phase 1 wiring follow-up Task 4 — D-002 a + β)

```python
import sys; sys.path.insert(0, '.claude/lib')
from atomy_toolkit.hybrid.superpowers import is_superpowers_available
available = is_superpowers_available()
print(
    f"superpowers: {'available — Brainstorm/Plan will delegate' if available else 'unavailable — using toolkit fallback'}"
)
```

모드가 **Brainstorm** 으로 결정된 경우 (조건 #4 or #5):
- 본 파일의 "Step 2 Mode Dispatch" 하위 "Brainstorm Mode" 섹션으로 진입

모드가 **Plan** 으로 결정된 경우 (조건 #6):
- 발견된 spec 경로를 Research 결과 블록에 `📄 Spec: {경로}` 로 표시
- "Plan Mode" 섹션으로 진입

### 1-B. Search (능동 탐색 — 티어 라우팅)

다음 순서로 정보를 수집하세요:

#### 1-B-1. 질의 분류 (router)

```text
python -c "
import sys
sys.path.insert(0, '.claude/lib')
import router
decision = router.classify('''$USER_QUERY''')
print('sources:', ','.join(sorted(decision.sources)))
print('matched:', decision.matched_patterns)
"
```

**🔥 Hot tier — 필수 읽기 (항상):**
1. `docs/plan.md` — 전체 계획과 현재 Phase
2. `docs/checklist.md` — 완료/미완료 항목
3. `docs/context.md` — 최근 중단 지점과 다음 Task

#### 1-B-2. ASMR 조회 (sources 에 'asmr' 포함 시)

**🟡 Warm tier — 조건부 읽기 (`.claude/memory/_index.md`가 존재할 때):**
4. `.claude/memory/_index.md` — 메모리 색인 + 참조 추적 테이블 읽기
5. **티어 라우팅 판단:**

   **[판단 A: Warm 충분성 검사]**
   Reader 단계에서 파악한 작업 도메인과 맥락 유형으로
   `_index.md`의 "도메인별 태그 색인"을 검색한다.

   → 관련 Warm 메모리가 **1개 이상** 발견되면:
     Warm tier에서만 선택 (최대 5개, 기존 우선순위 유지). 끝.

   **[판단 B: Cold 탐색 트리거 — 하나라도 해당 시]**
   B-1. Warm에서 관련 메모리 **0건** 발견
   B-2. 사용자 요청에 "이전 Phase", "예전에", "과거", "Phase N" 등 **시간적 과거 참조 키워드**가 포함됨
   B-3. 사용자가 **Cold 메모리 ID를 명시적으로 언급** (예: "DEC-003 관련")
   B-4. context.md의 "현재 Phase"와 사용자 요청의 **Phase가 다름**

   **🧊 Cold tier — 판단 B 충족 시:**
   6. `.claude/memory/archive/_archive_index.md` 읽기
   7. 도메인/태그 매칭으로 관련 Cold 메모리 식별
   8. **Cold에서 최대 2개** + **Warm에서 최대 3개** = 총 5개 유지
   9. 승격 필요 시 Ensemble 결과에서 제안

   - 선택 우선순위: (1) status=active (2) 동일 도메인 태그 (3) 최근 세션 번호

> 💡 `.claude/memory/` 폴더가 없으면 기존처럼 docs/ 3종만 읽고 진행하세요.
> 💡 `archive/` 폴더 또는 `_archive_index.md`가 없으면 Cold 탐색을 스킵하세요.

#### 1-B-3a. 로컬 memtemple 조회 (sources 에 'memtemple' 포함 시)

```text
python -c "
import sys
sys.path.insert(0, '.claude/lib')
import mempalace_client, json
from dataclasses import asdict
results = mempalace_client.search('''$USER_QUERY''', wings=['$(basename $PWD)'], top_k=10)
print(json.dumps([asdict(s) for s in results], ensure_ascii=False))
"
```

#### 1-B-3b. Federation 조회 (항상)

```text
python -c "
import sys
sys.path.insert(0, '.claude/lib')
import federation_client, json
from dataclasses import asdict
client = federation_client.get_federation_client()
results = client.search('''$USER_QUERY''', top_k=10)
print(json.dumps([asdict(s) for s in results], ensure_ascii=False))
"
```

현재는 Null stub 이 `[]` 를 반환하므로 결과가 비어있다. 미래 federation 활성화 시 자동으로 데이터가 채워진다.

#### 1-B-3c. Knowledge Graph 탐색 (sources 에 'graph' 포함 시)

Reader 단계에서 파악한 키워드로 그래프 이웃을 탐색하세요:

```python
import sys; sys.path.insert(0, '.claude/lib')
import graph_client
idx = graph_client.load_graph_index('.')
if idx:
    # 1) 키워드로 관련 노드 검색
    terms = graph_client.find_by_term(idx, '<핵심_키워드>')
    # 2) 발견된 노드의 1-hop 이웃 탐색
    for node_id in [t['local_id'] for t in terms[:3]]:
        neighbors = graph_client.get_neighbors(idx, node_id, max_hops=1)
        # MemorySnippet(source='graph') 로 변환하여 후보에 추가
    snippets = graph_client.graph_result_to_snippets(idx, [t['local_id'] for t in terms[:3]])
```

#### 1-B-3d. Data Source resolve (해당 시)

Reader 단계에서 정량 데이터 참조가 필요하다고 판단되면:

```python
import sys; sys.path.insert(0, '.claude/lib')
import data_source_resolver
sources = data_source_resolver.load_sources('.')
# privacy 확인 후 resolve
for src in sources:
    if data_source_resolver.check_privacy(src, requester_dept='<현재_부서>'):
        result = data_source_resolver.resolve(src, timeout=3)
```

> 정량 데이터는 **참조만** — 저장하지 않는다.

#### 1-B-4. 결과 병합 + Gemini rerank

ASMR + local memtemple + federation 스니펫을 합친다. 5개 초과 시 rerank 호출:

```text
python -c "
import sys
sys.path.insert(0, '.claude/lib')
import rerank
from mempalace_client import MemorySnippet
# candidates 는 위의 각 단계 결과를 합쳐서 만듦
# result = rerank.rerank(query, candidates, top_k=5)
"
```

실패하거나 후보가 5개 이하면 rerank 는 건너뛰고 소스별 쿼터 병합 (ASMR 3 + memtemple 2).

#### 1-B-5. Reader 단계 (기존)

상위 5 스니펫을 Reader 에 전달. 기존 로직 유지.

### 1-C. Ensemble (종합)

수집한 정보를 종합하여 다음 형식으로 요약하세요:

```
━━━ Research 결과 ━━━
🎛️ Mode: [Align / Trivial / Plan / Brainstorm]  (사유: [판정 근거 1줄])
📄 Spec: [docs/specs/... 경로 — Plan/Brainstorm 모드일 때만 표시]
📍 현재 Phase: [Phase X — 이름]
📋 직전 세션 요약: [1-2문장]
🎯 이번 요청의 의도: [Reader 분석 결과]

📚 참조한 메모리 (N건):
  🔥 [HOT] context.md — 직전 세션 중단 지점
  🟡 [WARM] DEC-001 제목 — 관련 이유
  🟡 [WARM] ARCH-001 제목 — 관련 이유
  🧊 [COLD] DEC-003 제목 — 아카이브에서 조회 (해당 시)
  🔗 [GRAPH] NODE-ID — N-hop 이웃 (해당 시)
  📊 [DATA] ds:source-id — 정량 데이터 참조 (해당 시)
  (메모리 미사용 시: "메모리 시스템 비활성")

🔄 Cold → Warm 승격 제안: (해당 시)
  • DEC-003: 이번 작업에 직접 관련 — 승격 권장

⚠️ 주의할 과거 결정:
  • [있을 경우만]

✅ Plan 단계에서 고려할 사항:
  • [과거 메모리에서 도출된 제약/참고 사항]
━━━━━━━━━━━━━━━━━━
```

---

## Step 2: Mode Dispatch

Research 결과 블록에 출력한 모드에 따라 아래 네 섹션 중 **정확히 하나**를 실행하세요.

### Step 2-A. Align Mode

**진입 조건:** 판정 테이블 #1 or #2

**Case #1 — `$ARGUMENTS` 비어있음:**

다음 프레이밍으로 출력:
```
원래 다음 진행사항은 {docs/plan.md 의 첫 미완료 Task} 입니다.
다른 원하시는 거 있나요?

  (A) 그대로 진행 — 계속할게요
  (B) 다른 작업 — 어떤 건지 말씀해주세요
```

- 응답 A → 그 Task 를 `$ARGUMENTS` 로 간주하고 Step 1 Reader 를 재실행 → 모드 재판정
- 응답 B → 새 작업 설명 받은 후 Step 1 Reader 재실행 → 모드 재판정 (보통 Brainstorm 로 빠짐)

**Case #2 — 입력이 plan 다음 Task 와 일치:**

```
원래 계획대로 {a} 진행합니다. 맞죠?

  (A) 맞아, 진행해 → Plan 또는 Brainstorm 모드로 진입 (spec 존재 여부에 따라)
  (B) 잠깐, 변경점 있어 → 어떤 변경인지 말씀해주세요 (Brainstorm 모드로 전환)
```

- 응답 A:
  - 관련 spec 존재 (glob `docs/specs/*<keyword>*.md`) → **Plan 모드** (Step 2-C) 로 이동
  - 관련 spec 없음 → **Brainstorm 모드** (Step 2-D) Case #5 프레이밍으로 이동
- 응답 B → Brainstorm 모드 섹션(Step 2-D)로 이동

### Step 2-B. Trivial Mode

**진입 조건:** 판정 테이블 #3

확인·질문 없이 Research 결과 블록만 출력하고, 바로 기존 경량 Plan 으로 진행:

> **경량 Plan 포맷:**
> - 어떤 파일을 수정/생성할 것인지
> - 각 파일에서 무엇을 변경할 것인지
> - 예상되는 위험요소는 무엇인지
> - 테스트 계획은 무엇인지

Plan 제시 직후 사용자 승인을 1회 받고 Step 3 Implement 로 진행.

**Trivial 오판 escalate:** Step 3 Verification Gate 에서 테스트 fail 시 → "생각보다 복잡하네요. Plan 모드로 전환할게요" 출력 후 Step 2-C 로 전환.

### Step 2-C. Plan Mode

상세 지침은 본 파일 하단 **"Step 2-C 세부: Plan Mode 실행 지침"** 섹션 참조.

### Step 2-D. Brainstorm Mode

상세 지침은 본 파일 하단 **"Step 2-D 세부: Brainstorm Mode 실행 지침"** 섹션 참조.

**중요:** 모든 모드에서 승인 없이는 Step 3 Implement 로 넘어가지 마세요.

---

## Step 2-D 세부: Brainstorm Mode 실행 지침

<!-- HARNESS:STEP-RPI-2D -->

Hybrid 진입: superpowers plugin 가용 시 brainstorming skill 로 위임, 부재 시 toolkit fallback (`atomy_toolkit.brainstorm.run_brainstorm`) 호출. 양쪽 path 가 동일한 3-key dict (questions / decisions / spec_path) 반환.

```python
import sys; sys.path.insert(0, '.claude/lib')
from atomy_toolkit.hybrid.superpowers import brainstorm
# `query` = 사용자의 다음작업 입력. Hybrid wrapper 가 분기.
result = brainstorm(query)
print(
    f"brainstorm: {len(result['questions'])} questions, spec={result['spec_path']}"
)
```

### D-1. 진입 프레이밍

Reader 판정 #4 (계획 불일치):
```
원래 계획은 "{plan 다음 Task}" 인데, "{$ARGUMENTS}" 를 말씀하셨네요.
먼저 의도를 정리해볼게요. 몇 가지 여쭤볼게요.

(질문 1/?) 지금 계획을 변경하시는 건가요, 아니면 이번만 잠깐 우회하시는 건가요?
  (A) 계획 변경 — plan.md 를 업데이트할게요
  (B) 일회성 우회 — 끝나면 원래 Task 로 돌아갑니다
  (C) 사실은 둘 다 필요 — 분리해서 처리할게요
```

Reader 판정 #5 (신규 기능 + spec 없음):
```
신규 기능이네요. 바로 구현하기 전에 몇 가지 정리해볼게요.

(질문 1/?) 이 기능의 한 줄 목적이 뭔가요? (누구에게 어떤 가치를 주나요?)
```

### D-2. 질문 루프 규칙

다음 규칙을 **모든 질문에 적용**:

1. **한 번에 한 질문** — 한 응답에 여러 질문 금지. 주제가 크면 분해해서 여러 메시지로
2. **선택지 우선** — 가능하면 A/B/C 포맷, open-ended 는 꼭 필요할 때만
3. **2-3 접근법 제시** — 설계 분기가 있는 질문은 trade-off 와 추천을 선택지에 녹여서:
   ```
   세 가지 방법이 있어요:

   (A) 폴링 — 간단, 실시간성 낮음
   (B) WebSocket — 실시간성 좋음, 인프라 복잡
   (C) SSE — 중간, 단방향이라 이 경우 충분

   저는 (C) 추천 — 단방향이고 HTTP 위에 얹히니...
   ```
4. **user_level 톤 적용** — Step 0 에서 감지한 `user_level` 을 모든 질문에 반영:
   - `beginner`: "A (B) 어쩌구" 대신 "(A) 이렇게 하면 ~~ 장점: 쉬워요"
   - `advanced`: 용어·약어 자유 사용
5. **scope 폭발 감지** — 사용자가 중간에 "X 도 Y 도 Z 도" 하면서 scope 를 늘리면:
   ```
   ⚠️  이 기능 하나에 X, Y, Z 세 가지가 들어가네요. 각자 독립적이라
   한 spec 에 묶으면 작업 분해가 흐려집니다.

     (A) 지금은 X 만 진행, Y/Z 는 별도 spec 으로 분리
     (B) 셋 다 강하게 연결 — 이유 알려주세요
   ```

### D-3. Spec 문서 생성

질문 루프가 수렴하면 **자동으로 spec 파일 생성**:

- 경로: `docs/specs/YYYY-MM-DD-<topic-slug>.md`
- `YYYY-MM-DD`: 생성일 (시스템 날짜)
- `<topic-slug>`: Reader 가 첫 질문 단계에서 제안 → 사용자가 수정 가능 (kebab-case, 영문 권장)
- 같은 날 같은 slug 재사용 시 `-v2`, `-v3` suffix 자동 추가

**템플릿:** `templates/docs-plans-template.md` 옆에 위치한 spec 템플릿 또는 `/new` T02.5 가 생성한 `docs/specs/_TEMPLATE.md` 를 참조. 다음 8섹션 준수:

1. 문제 정의
2. 사용자 스토리
3. 검토된 접근법 (brainstorming 으로 도출된 A/B/C 표)
4. 입·출력 계약
5. 비기능 요구 (해당 시만)
6. 엣지 케이스
7. 수용 기준 (AC)
8. 범위 외 (Non-Goals)

**frontmatter:**
```yaml
---
id: SPEC-YYYY-MM-DD-<SLUG>
title: [한 줄]
status: draft
created: YYYY-MM-DD
mode: Brainstorm
user_level: {레벨}
---
```

### D-4. Spec Self-Review (인라인)

spec 저장 직후 **fresh eyes 로 4가지 체크**:

1. **Placeholder 스캔** — "TBD", "TODO", 빈 섹션, 공백 bullet → 채우거나 "해당 없음" 명시
2. **내부 모순** — AC 가 입·출력 계약과 충돌하는지 확인
3. **범위** — 단일 spec 으로 커버 가능한 크기인지. 아니면 decompose 제안:
   ```
   ⚠️ 이 spec 이 독립 서브시스템 N 개를 담고 있습니다. 다음 중 하나로 진행 권장:
     (A) 첫 서브시스템만 이 spec 에 유지, 나머지는 후속 spec 으로 분리
     (B) 현재 그대로 진행 — 이유 알려주세요
   ```
4. **모호성** — 두 가지로 해석될 수 있는 요구사항을 하나로 고정

문제 발견 시 **인라인 수정** 후 사용자에게:
```
Spec 작성 완료 — docs/specs/YYYY-MM-DD-<slug>.md
검토해보시고 수정 원하시면 말씀해주세요. OK 하시면 Plan 모드로 넘어갑니다.
```

### D-5. Skip 지원

사용자가 Brainstorm 루프 중 `skip brainstorm` / `건너뛰어` 입력 시:

1. 지금까지의 질문-응답을 간략 spec 으로 요약 (8섹션 중 최소 문제 정의 / AC / 범위 외만 채움)
2. `docs/specs/YYYY-MM-DD-<slug>.md` 에 저장, frontmatter 에 `status: skipped-partial`
3. "Spec 간략본 저장했습니다. Plan 모드로 넘어갑니다." 출력
4. Plan Mode (Step 2-C) 로 자동 전환

### D-6. 중도 이탈 처리

사용자가 Brainstorm 중 다른 주제로 빠지거나 명시적 중단 시:

1. 지금까지의 답변을 `docs/specs/YYYY-MM-DD-<slug>.draft.md` 로 저장 (`.draft.md` 접미어)
2. 다음 `/rpi` 호출 시 Reader 가 `.draft.md` 감지하면:
   ```
   이전에 정리하던 스펙이 있네요 — {slug} (작성 N/8 섹션)
     (A) 이어서 계속
     (B) 새로 시작 (draft 는 남겨둠)
     (C) draft 삭제 후 새로 시작
   ```

### D-7. Plan 모드로 전환

사용자 승인 응답이 들어오면:

1. spec frontmatter `status: draft` → `status: approved` 로 갱신
2. `docs/plan.md` 로드맵 업데이트 필요한지 판정 — 필요하면 사용자에게 질문:
   ```
   이 기능을 docs/plan.md 의 Phase {N} Task 로 추가할까요?
     (A) 예 — Phase {N} 에 추가
     (B) 아니오 — 이번만 진행
   ```
3. Plan Mode (Step 2-C) 로 자동 연속 진입 (사용자가 `/rpi` 재호출 불필요)

---

## Step 2-C 세부: Plan Mode 실행 지침

<!-- HARNESS:STEP-RPI-2C -->

Hybrid plan writer: superpowers plugin 가용 시 plan-writing skill 로 위임, 부재 시 toolkit fallback (`atomy_toolkit.plan_writer.run_write_plan`) 호출.

```python
import sys; sys.path.insert(0, '.claude/lib')
from atomy_toolkit.hybrid.superpowers import write_plan
plan_path = write_plan(spec_path)
print(f"plan written to {plan_path}")
```

### C-1. Spec 읽기

- 진입 경로 A (Reader 조건 #6): Research 블록에 표시된 `📄 Spec: {경로}` 의 파일을 Read
- 진입 경로 B (Brainstorm D-7 자동 진입): 방금 생성한 spec 파일을 Read

spec 의 모든 섹션을 읽고, 특히 "수용 기준 (AC)" 과 "입·출력 계약" 을 다음 단계 입력으로 사용.

### C-2. TDD-capability 판정

Plan 작성 **전에** 세 신호로 Task 별 테스트 가능 여부 판정:

| 신호 | 판정 |
|------|------|
| 테스트 프레임워크 존재 (`pytest`/`jest`/`vitest`) **AND** 작업이 비즈니스 로직·데이터 변환·알고리즘 | **TDD** (5-Step) |
| 테스트 프레임워크 존재 **AND** 작업이 UI 스타일·설정 파일·문서·빌드 설정 | **Non-TDD** (3-Step) |
| 테스트 프레임워크 없음 | **Non-TDD** 전부 |
| 여러 Task 가 다른 성격 | Task 별 독립 판정 (한 plan 에 혼재 허용) |

판정 확인 방법:
- `pytest` 존재: `Glob` 로 `**/pytest.ini`, `**/pyproject.toml` (tool.pytest 섹션) 검색
- `jest`/`vitest` 존재: `package.json` scripts 에서 `test` 명령 확인

판정 결과를 plan 문서 헤더 `**TDD:**` 필드에 기록.

### C-3. Plan 문서 생성

- 경로: `docs/plans/YYYY-MM-DD-<topic-slug>.md` (spec 과 동일 slug)
- 템플릿: `templates/docs-plans-template.md` 을 기준으로 작성

**헤더 필수 필드:**
```markdown
# [기능명] Implementation Plan

> **For agentic workers:** ... (템플릿 문구 그대로)

**Spec:** `docs/specs/YYYY-MM-DD-<slug>.md`
**Goal:** [한 문장]
**Architecture:** [2-3 문장]
**Tech Stack:** [주요 도구]
**TDD:** Task 1,2: TDD / Task 3: Non-TDD (사유)
**Git:** [frequent commits / no git (save only)]
```

**Task 포맷:**
- TDD Task → 5-Step (Write test → Run fail → Implement → Run pass → Commit)
- Non-TDD Task → 3-Step (변경 작성 → 수동 검증 → Commit)
- git 없는 프로젝트 → Commit Step 전부 생략

**각 Task 는 `**AC 매핑:**` 필드로 spec 의 AC 번호를 참조**.

### C-4. No-Placeholder 규칙

plan 문서에 **절대 쓰지 않을 것** (writing-plans 의 핵심 discipline):

- ❌ "TBD", "TODO", "implement later", "fill in details"
- ❌ "적절한 에러 핸들링 추가" / "엣지 케이스 처리"
- ❌ "위에 대한 테스트 작성" (실제 테스트 코드 없이)
- ❌ "Task N 과 유사" (코드를 다시 쓸 것)
- ❌ 어느 Task 에도 정의되지 않은 함수·타입 참조

코드가 필요한 Step 에는 **반드시 실제 코드 블록**, 명령어 Step 에는 **반드시 exact command + expected output**.

### C-5. Plan Self-Review (인라인)

plan 작성 직후 3가지 체크:

1. **Spec 커버리지** — spec 의 각 AC 번호가 어느 Task 에 매핑되는지 확인. 빠진 AC 있으면 Task 추가 (TBD 로 남기지 말 것 — 실제 Task 작성)
2. **Placeholder 스캔** — C-4 블랙리스트 grep. 발견 시 실제 내용으로 교체
3. **타입·이름 일관성** — Task 1 에서 `parseOrder()` 라 해놓고 Task 3 에서 `parseOrderData()` 면 수정

문제 발견 시 인라인 수정. 재리뷰 불필요.

### C-6. 실행 방식 선택

Plan 승인 직후 **1회 질문**:

```
Plan 작성 완료 — docs/plans/YYYY-MM-DD-<slug>.md
실행 방식 두 가지:

  (A) Inline (추천) — 이 세션에서 Task 하나씩 실행, Task 사이 확인
  (B) Subagent-driven — 각 Task 를 fresh subagent 에 dispatch, Task 간 리뷰

간단한 기능은 (A), 파일 많고 독립적 Task 가 여럿이면 (B). 어느 쪽?
```

**예외 — user_level=beginner:** 이 질문을 **숨기고** 자동으로 (A) Inline 선택. (subagent-driven 은 advanced 사용자용 개념)

선택 결과를 `docs/context.md` 의 "실행 방식" 필드에 기록 → `/handoff` 시에도 동일 전략 유지.

#### C-6 모델 라우팅 (자동 판정 + override)

실행 방식(inline/subagent)과 **별개 레이어**로, 각 Task 를 **claude-inline vs codex-dispatch** 로
자동 판정한다. claude 로 라우팅된 Task 는 이 세션에서 inline(또는 subagent) 구현, codex 로
라우팅된 Task 는 `/implement` 로 위임한다. (spec: `docs/specs/2026-05-30-s4-model-routing.md`)

1. **override 충돌 점검**: 사용자 입력에 줄머리 `>>claude` 와 `>>codex` 가 둘 다 있으면
   `parse_model_override` 가 `"conflict"` 를 반환한다 → **라우팅하지 말고 사용자에게 재질의**.
2. **Task별 판정** (python-level — shell 호출 없음). `USER_INPUT` = 사용자의 `/rpi` 입력 문자열,
   `TASK_BLOCK` = 네가 plan 에서 읽은 한 `## Task N` 블록 텍스트:

```python
import sys; sys.path.insert(0, '.')
from atomy_toolkit.dispatcher import routing
override = routing.parse_model_override(USER_INPUT)  # 'conflict' 면 위 1번에서 정지
tag = routing.parse_model_tag(TASK_BLOCK)
r = routing.decide_model(TASK_BLOCK, plan_tag=tag,
                         override=(override if override in ('claude', 'codex') else None))
sensitive = routing._is_cascade_sensitive(routing._strip_fences(TASK_BLOCK))
warn = ''
if r.target == 'codex' and sensitive and r.source in ('override', 'plan_tag'):
    warn += '  ⚠️ cascade-sensitive → codex (override/tag)'
if routing.model_tag_malformed(TASK_BLOCK):
    warn += '  ⚠️ 잘못된 **Model:** 태그 — heuristic fallback'
print(f'{r.target}  ({r.source}/{r.reason_code}){warn}')
```

   각 Task 의 출력을 모아 `Task N → {target} ({source}/{reason_code})` 표로 사용자에게 보고한다.
   판정 출처는 **override > plan 태그(`**Model:** claude|codex`) > heuristic**(cascade-민감 → claude /
   TDD-capable → codex / 그 외 → claude 보수 기본) 순.
3. **실행**: codex Task 는 `/implement` 위임(사람이 `/review` 로 검토), claude Task 는 inline 구현.
   기존 inline vs subagent 선택은 claude 경로 안에서 그대로 유지.

### C-7. Implement 진입

사용자 승인 응답 받으면 Step 3 Implement 로 진행.

---

## Compliance Audit v2 Carry-Forward Contract

Step 0 must resolve `user_level` from project rule files first, then continue with the normal fallback behavior.

During Step 1 Research, read compliance carry-forward before choosing the next implementation task:

1. Inspect `docs/context.md` for `closure_status` and `compliance_audit`.
2. If `compliance_audit` points to an audit log, read that exact file first.
3. If there is no pointer, fall back to the highest numeric session in `.claude/memory/compliance-audit/`.
4. If numeric session parsing is impossible, use latest modified audit log as the final fallback.

If the previous handoff had `closure_status: compliance_blocked`, the Research result must include an `Unresolved Findings` section. HIGH, FAIL, and CRITICAL findings take priority over roadmap tasks unless the user explicitly asks to override the carry-forward work.

---

## Dispatcher Carry-Forward Contract

Step 1 Research 중, compliance carry-forward 를 읽은 직후 dispatcher in-flight
WorkOrder 도 확인한다 (`/handoff` STEP 2.5.5 가 박아둔 것).

```python
import sys; sys.path.insert(0, '.claude/lib')
from pathlib import Path
from atomy_toolkit.dispatcher import parse_carryforward

cf = parse_carryforward(Path("docs/context.md").read_text(encoding="utf-8"))
```

- `cf.has_work and cf.priority == "preempt"` (blocked/failed) → Research 결과의
  `⚠️ 주의할 과거 결정` **위**에 `🔧 In-Flight WorkOrder (preempt)` 줄을 추가하고,
  해당 WorkOrder 를 **로드맵 Task 보다 우선**으로 surface. (사용자가 명시적으로
  override 요청 시 제외 — compliance carry-forward 와 동일 규칙.)
- `cf.has_work and cf.priority == "informational"` → `🔧 In-Flight WorkOrder (info)`
  줄만 추가, 우선순위 변경 없음.
- `dispatcher_status: none` / 블록 부재 → 변화 없음.

---

## Step 3: Implement (실행)
승인을 받으면 계획대로 실행하세요.

### 3-A. Verification Gate — 증거 없는 완료 선언 금지 ⚠️

구현 완료를 사용자에게 선언하기 **전에 반드시** 다음 중 최소 2가지를 실제로 수행하고 **출력 결과(증거)** 를 보고해야 합니다:

1. **테스트 실행** — `pytest` / `npm test` 등 관련 테스트를 실제로 돌리고 PASS 확인
2. **빌드/린트** — `ruff check` / `npm run build` / `tsc --noEmit` 등을 실행
3. **실제 실행 검증** — CLI 실행·HTTP 요청·브라우저 렌더 등 End-to-End 확인 (해당 시)

**루프 규칙:**
- 실패 시 원인을 스스로 진단 → 수정 → 재실행. **사용자에게 완료 보고 전까지 이 루프를 벗어나지 않는다.**
- 테스트·린트 도구가 프로젝트에 없는 경우 예외: 사용자에게 "검증 수단 부재 — 수동 확인 필요" 를 명시적으로 통지.
- 마지막 실행의 **실제 출력 스니펫** 을 보고에 포함해야 "완료" 로 간주됩니다.

> ❌ "아마 동작할 겁니다", "수정했습니다" 만으로 완료 선언 금지
> ✅ "pytest 24 passed / ruff clean — 증거: [출력]" 처럼 근거 제시

### 3-B. 후속 기록

1. `docs/checklist.md`에서 완료 항목을 체크하세요
2. `docs/context.md`에 변경사항과 이유를 기록하세요 (Plan/Brainstorm 모드였다면 `현재 mode`, `실행 방식(inline/subagent)` 필드도 기록)
3. **Plan 문서 체크박스 갱신** — Plan/Brainstorm 모드였다면 `docs/plans/YYYY-MM-DD-<slug>.md` 의 완료한 Task Step 을 `- [ ]` → `- [x]` 로 변경
   - **모든 Task 완료 시**: `**Status:** shipped` 마커는 **직접 적지 말고** seal/reconcile/`/review` approve 에 위임한다(조기 마커로 다음 Task 가 거짓 완료되는 것 방지).
4. 변경 내용을 한줄로 요약해주세요
5. 메모리로 저장할 의사결정/버그/학습이 있다면, `/handoff` 시 자동 처리됩니다
6. **이번 세션에 발생한 버그/린트 실패/테스트 실패가 있다면** `.claude/memory/learnings/recurring-mistakes.md` 에 재발 방지용 1행을 추가하세요 (파일이 없으면 생성)
7. Plan 문서에 미완료 Task 가 남아있으면 `/handoff` 가 `docs/context.md` 의 "다음 Task" 로 이전 (별도 작업 불필요)

**텔레메트리 (opt-in, 로컬 전용):** 사용자가 동의한 경우에만 기록됩니다. 미동의 시 no-op.

```python
import sys; sys.path.insert(0, '.claude/lib')
from atomy_toolkit.telemetry import record  # opt-in 시에만 기록, 아니면 no-op
record("command_invoked", command="rpi")
record("rpi_mode", command="rpi", mode="<Align|Trivial|Plan|Brainstorm>")
record("verification_gate", command="rpi", outcome="<pass|fail>")
# record() 가 유일한 동의 게이트 — is_enabled() 사전 체크 금지 (P2-12/AC-14)
```
