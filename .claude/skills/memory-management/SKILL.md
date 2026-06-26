---
name: memory-management
description: .claude/memory/ 폴더의 원자적 메모리 파일 생성, 수정, 검색 시 적용되는 규칙. memory, 기억, 맥락, context, handoff, 인계, 이전 결정, 과거 세션 키워드가 관련될 때 활성화.
---

# 메모리 관리 규칙 (ASMR v4.0 — Knowledge Fabric)

> ASMR = Agentic Search and Memory Retriever
> 세션 간 장기기억을 원자적 마크다운 파일로 관리하는 시스템

---

## 1. 메모리 디렉토리 구조 (3-Tier)

```
.claude/memory/
├── _index.md              # [Warm] 색인 (참조 추적 포함) — 검색 진입점
├── decisions/             # [Warm] 의사결정: "왜 A 대신 B를 선택했는가?"
├── architecture/          # [Warm] 시스템 구조, 데이터 흐름, 공식
├── bugs/                  # [Warm] 버그 발생-원인-해결 기록
├── learnings/             # [Warm] 외부 API/라이브러리 특성, 시행착오
└── archive/               # [Cold] 아카이브 저장소
    ├── _archive_index.md  # Cold 전용 색인
    ├── decisions/
    ├── architecture/
    ├── bugs/
    └── learnings/
```

### 티어 정의

| 티어 | 위치 | 로드 정책 | 최대 크기 |
|------|------|-----------|----------|
| **Hot** | `docs/context.md` | 항상 로드 (매 세션) | 4 KB, 3세션분 |
| **Warm** | `.claude/memory/` (archive/ 제외) | `/rpi` 선택 로드 (최대 5파일) | active 50개 |
| **Cold** | `.claude/memory/archive/` | 라우팅 조건 충족 시만 | 무제한 |

---

## 2. 메모리 파일 형식 규칙

모든 메모리 파일은 **YAML frontmatter + 4단 본문** 구조를 따른다.

### 필수 필드 (frontmatter)

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | 고유 ID (예: DEC-001) |
| `category` | string | decision / architecture / bug / learning / session |
| `title` | string | 한 줄 제목 (한글 가능) |
| `tags` | list | 검색용 태그 (도메인명, 기술명 등) |
| `created` | date | Document Date — 파일 생성일 (YYYY-MM-DD) |
| `event_date` | date | Event Date — 실제 결정/발생일 (YYYY-MM-DD) |
| `session` | int | 세션 번호 |
| `status` | string | active / superseded / archived |
| `project` | string | 프로젝트명 |
| `domain` | string | DDD 도메인명 |

### 선택 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `superseded_by` | string | 이 메모리를 대체한 메모리 ID |
| `references` | list | 관련 메모리 ID 목록 |
| `tier` | string | warm / cold (기본값: warm, 명시하지 않으면 warm) |
| `reactivated_from` | string | 승격 시 이전 상태 (archived) |
| `reactivated_session` | int | 승격이 발생한 세션 번호 |
| `last_referenced_session` | int | 마지막으로 /rpi에서 참조된 세션 번호 |

### 본문 구조 (4단)

```markdown
## 맥락
[발생 배경 — 왜 이 정보가 생겼는가]

## 결정 / 내용
[핵심 내용 — 무엇을 결정했거나 발견했는가]

## 근거
[선택 이유, 대안 비교, 참고 자료]

## 영향받는 파일
[관련 코드 경로 — 어떤 파일이 변경되었는가]
```

---

## 3. 카테고리 분류 규칙

| 카테고리 | 저장 기준 (이 질문에 "예"면 해당) | 예시 |
|---------|-------------------------------|------|
| **decisions/** | "왜 A 대신 B를 선택했는가?" 형태의 정보 | API 설계, 라이브러리 선정, 알고리즘 선택 |
| **architecture/** | 시스템 구조, 데이터 흐름, 공식 등 변동이 적은 참조 지식 | DDD 매핑, 스코어링 공식, 데이터 파이프라인 |
| **bugs/** | 버그 발생-원인-해결 3요소가 모두 있는 경우 | 런타임 에러, 데이터 불일치, 엣지케이스 |
| **learnings/** | 외부 도구/API/라이브러리의 특성, 제약, 우회 방법 | API rate limit, regex 패턴, 라이브러리 버그 |

---

## 4. ID 부여 규칙

- 형식: `{카테고리약어}-{3자리 일련번호}`
- 약어 매핑:
  - decisions → `DEC`
  - architecture → `ARCH`
  - bugs → `BUG`
  - learnings → `LEARN`
- `_index.md`에서 해당 카테고리의 마지막 번호를 확인하고 +1
- 번호는 카테고리 내에서 독립적 (DEC-001과 BUG-001은 공존)
- 파일명: `{ID}_{영문하이픈슬러그}.md` (예: `DEC-001_avail-zero-scoring.md`)

---

## 5. 3단계 기억 관계 판단 규칙

### Update (갱신)

**조건**: 기존 메모리에 기술된 사실이 더 이상 유효하지 않을 때
**방법**:
- 경미한 변경: 해당 파일의 내용을 수정하고 `event_date`를 갱신
- 중대한 변경: `status`를 `superseded`로 변경하고, 새 메모리 생성 후 `superseded_by` 기록

### Extend (확장)

**조건**: 기존 메모리의 결론은 유효하지만 디테일이 추가될 때
**방법**:
- 해당 파일에 새 섹션을 추가하거나 기존 섹션을 보강
- `event_date`를 가장 최근 확장 날짜로 갱신

### Derive (파생)

**조건**: 이번 세션의 결과가 기존 메모리 어느 것에도 해당하지 않는 새 지식일 때, 또는 여러 메모리를 종합하여 새 패턴/아키텍처가 도출될 때
**방법**:
- 새 파일 생성 (적절한 카테고리 폴더에)
- `references`에 원본 메모리 ID 기록

---

## 6. 메모리 생성 문턱 (Threshold)

아래 질문 중 하나라도 "예"일 때만 메모리를 생성/수정한다:

1. "이 정보가 다음 세션 이후에도 필요한가?"
2. "이 결정을 나중에 왜 그랬는지 물을 수 있는가?"
3. "시스템 구조나 데이터 흐름이 바뀌었는가?"
4. "버그를 고쳤고, 같은 유형의 버그가 재발할 수 있는가?"
5. "외부 도구/API에 대해 새로 알게 된 것이 있는가?"

**메모리로 만들지 않는 것**: 오타 수정, import 정리, 단순 리팩토링, 주석 추가 등 사소한 변경

---

## 7. 토큰 절약 규칙

- `/rpi`에서 메모리 조회 시 **총 최대 5개 파일**만 읽는다
  - Warm만 탐색 시: 최대 5개
  - Cold도 탐색 시: Warm 최대 3개 + Cold 최대 2개 = 5개
- 반드시 `_index.md`의 태그 색인으로 1차 필터링한 뒤 본문을 읽는다
- `docs/context.md`는 최근 3세션분만 유지한다 (이전 기록은 mempalace 가 담당)
- 선택 우선순위: (1) status=active (2) 동일 도메인 태그 (3) 최근 세션 번호

---

## 8. _index.md 관리 규칙

- 메모리 파일을 생성/수정/삭제할 때 **반드시** `_index.md`를 동기화한다
- "도메인별 태그 색인" 섹션은 `/rpi` Search 단계의 핵심 참조점이므로 정확히 유지
- `status=superseded` 항목은 목록에서 ~~취소선~~ 또는 `(superseded)` 표기
- `status=archived` 항목은 `_index.md`에서 제거하고 `_archive_index.md`로 이동
- 카테고리별 목록에 Cold 카운트를 병기한다: `### decisions/ (Warm: 2건, Cold: 1건)`

### _index.md 헤더 형식

```markdown
# Memory Index
> 최종 업데이트: [날짜] (세션 N)
> Warm 메모리: N개 (active: N, superseded: 0)
> Cold 아카이브: M개
```

### 참조 추적 테이블

`_index.md` 하단에 참조 추적 테이블을 유지한다:

```markdown
## 참조 추적
| ID | 마지막 참조 세션 | 비활성 세션 수 |
|----|-----------------|--------------|
| DEC-001 | 8 | 0 |
| LRN-001 | 3 | 5 |
```

### _archive_index.md 관리 규칙

- Cold tier로 강등된 메모리는 **반드시** `_archive_index.md`에 등록한다
- 형식은 `_index.md`와 동일 (카테고리별 목록 + 도메인별 태그 색인)

---

## 9. 아카이브 정책 (3-Tier)

### 강등 규칙 (Warm → Cold)

다음 조건 중 하나라도 해당하면 `/handoff` 시 자동 강등한다:

1. `status: superseded` → 즉시 `archive/{category}/`로 이동
2. 10세션 이상 미참조 (참조 추적 테이블 기준) → `status: archived`, `archive/{category}/`로 이동
3. Warm active 50개 초과 → 비활성 세션 수가 높은 순으로 강등 (40개 이하까지)

**강등 수행 절차:**
1. 대상 파일의 `status`를 `archived`, `tier`를 `cold`로 변경
2. 파일을 `.claude/memory/archive/{category}/`로 이동
3. `_index.md`에서 해당 항목 제거 + 참조 추적 테이블에서 삭제
4. `_archive_index.md`에 해당 항목 추가
5. 강등된 메모리 목록을 `/handoff` 인계 보고에 포함

> 강등은 물리적 이동이다 — 파일이 두 곳에 동시 존재하면 안 된다.

### 승격 규칙 (Cold → Warm)

다음 조건 중 하나라도 해당하면 승격한다:

1. `/rpi` 라우팅에서 Cold 접근이 트리거되고 해당 메모리가 실제 작업에 활용됨
2. 사용자가 Cold 메모리 ID를 명시적으로 언급 (예: "DEC-003 관련")
3. 새 메모리의 `references`가 Cold 메모리 ID를 참조

**승격 수행 절차:**
1. 파일을 `archive/{category}/` → `memory/{category}/`로 이동
2. frontmatter 갱신: `status: active`, `tier: warm`, `reactivated_from: archived`, `reactivated_session: {N}`
3. `_index.md`에 추가 + 참조 추적 테이블에 등록
4. `_archive_index.md`에서 제거

### 하위 호환

- `archive/` 폴더가 없으면 v2.0처럼 동작 (flat structure, 강등 로직 스킵)
- `_archive_index.md`가 없으면 Cold tier 탐색 스킵
- 기존 `status: archived` 메모리 중 물리적으로 Warm에 남아있는 것은 다음 `/handoff` 시 자동으로 `archive/`로 이동

---

## 10-A. 반복 실수 로그 (recurring-mistakes.md) — 복리 학습 규칙

`.claude/memory/learnings/recurring-mistakes.md` 는 일반 learnings 메모리와 별개의 **단일 진실 소스** 로 관리합니다.

### 갱신 의무 (Hard Rule)

이번 세션에서 다음 중 하나라도 발생했다면 `/handoff` 에서 반드시 1행 이상 추가해야 합니다:
- 런타임 버그 수정
- 테스트 실패 후 수정
- 린트/타입체크 실패 후 수정
- `/rpi` Verification Gate 실패 후 재시도

갱신 누락 시 `/handoff` STEP 3 인계 보고에 🟡 경고 표시. 반복 누락은 learnings 시스템의 의미를 훼손합니다.

### 기록 형식

표 형식(`| 날짜 | 도메인 | 실수 | 원인 | 재발 방지책 |`)만 사용. 서술형 금지. 한 실수 = 한 행.

### 일반 learnings/와의 차이

| 구분 | recurring-mistakes.md | learnings/LRN-*.md |
|------|----------------------|--------------------|
| 목적 | 재발 방지용 빠른 체크리스트 | 외부 API·라이브러리 지식 축적 |
| 형식 | 단일 파일 표 | 파일별 원자적 4단 구조 |
| 갱신 | 오류 발생 시 즉시 | Threshold 충족 시 |
| 참조 | `/rpi` Reader 단계에서 훑어보기 권장 | `/rpi` Search 단계에서 선택 조회 |

### /rpi 활용

Reader 단계가 파악한 작업 도메인이 이 파일의 "도메인" 열과 매칭되면, 해당 행(들)을 Plan 단계의 "주의할 과거 결정" 섹션에 인용합니다. 이 파일은 항상 Warm tier 에 유지되며 강등되지 않습니다.

---

## 10. 참조 추적

`_index.md`의 참조 추적 테이블은 `/handoff` 시마다 갱신된다:

- 이번 세션에서 `/rpi`가 읽은 메모리 → `마지막 참조 세션` = 현재 세션 번호
- 읽히지 않은 메모리 → `비활성 세션 수` += 1
- `/handoff`의 Update/Extend/Derive에서 수정된 메모리도 참조로 간주
- 비활성 세션 수가 10에 도달하면 강등 대상으로 표시

### 참조 판정 기준

- `/rpi` Step 1-B에서 실제로 파일을 Read한 경우만 "참조"로 간주
- `_index.md`에서 ID를 확인만 한 것은 참조로 간주하지 않음
- `/handoff`에서 Update/Extend/Derive 대상이 된 메모리는 참조로 간주

---

## 11. memtemple 연동 — "무엇을 이야기했는가"

ASMR 은 "왜" 를 저장하고, memtemple 은 "무엇을 이야기했는지" 를 저장한다. 두 시스템은 서로의 저장소를 직접 건드리지 않으며 `/rpi`·`/handoff` 에서만 만난다.

### 역할 분담

| 질의 유형 | 담당 |
|---|---|
| "왜 A 대신 B를 선택했는가?" | ASMR decisions/ |
| "이 시스템은 어떻게 구성돼 있지?" | ASMR architecture/ |
| "이 버그 전에 본 적 있나?" | ASMR bugs/ + memtemple |
| "지난주에 auth 논의 어떻게 됐지?" | memtemple |
| "3개월 전 rate limit 이슈" | memtemple |
| "이건 어떻게 해결하면 되지?" | ASMR + memtemple 양쪽 |

### 위치

- 기본: `~/.memtemple/` (user-wide vault root)
- 오버라이드: `MEMTEMPLE_HOME` 환경변수
- vault 구조: `~/.memtemple/<wing>/{sessions,decisions,docs}/`

### /handoff 가 하는 일

매 세션 종료 시 STEP 2.7 에서 `atomy-toolkit memtemple save --plugin claude_code` 가 호출되어 현재 세션의 JSONL 을 vault `<wing>/sessions/` 에 markdown drawer 로 박는다. drawer frontmatter 에 wing/room/source_id/captured_at/turn_pairs 등 메타데이터가 태깅된다. T-v1.x-A.4 부터 단일 leg (legacy mempalace mine 2-leg 대체).

### /rpi 가 하는 일

질의가 들어오면 router 가 ASMR / memtemple / both 로 분류한다 (router 의 `_MEMTEMPLE_PATTERNS`). memtemple 분기 시 `mempalace_client.search()` shim 이 호출되며, 이는 내부적으로 `atomy_toolkit.memtemple.core.search.bm25_search` 로 위임된다. 후보가 모이면 Gemini 3.1 Flash 로 재랭킹한다. 모든 단계는 silent fallback — vault 부재 또는 Gemini 장애 시 ASMR 만으로 응답한다.

### 누적 세션 백필

handoff 도입 이전의 누적 JSONL 은 `atomy-toolkit memtemple backfill --plugin claude_code --apply` 로 일괄 이관 가능 (T-v1.x-A.6, 2026-05-20).

### 미래: Federation

교차 사용자 교차 vault 조회는 `federation_client.py` Null stub 으로 예비. v1.x 후속.

## 12. Knowledge Graph 연동 — "어떻게 연결되는가"

### 디렉토리

```
.claude/memory/graph/
├── graph_meta.yaml        # 네임스페이스 + 설정
├── graph_index.json       # 빌드된 그래프 (자동 생성)
├── glossary/              # 도메인 용어 정의
└── sources/               # data_source YAML (정량 데이터 참조)
```

### frontmatter `links` 필드

메모리 파일에서 명시적 엣지를 선언:

```yaml
links:
  - target: ARCH-001
    type: depends_on
    annotation: 아키텍처 의존성
```

### wikilinks

본문에서 `[[TARGET-ID]]` 또는 `[[TARGET-ID|edge_type]]` 으로 암시적 엣지 생성. `[[glossary:term]]` 으로 용어 참조.

### /graph 커맨드

`/graph` 커맨드로 그래프를 탐색, 수동 엣지 추가/제거, 용어 검색, 고아 감지 등을 수행.

### /rpi 그래프 탐색

라우터가 `graph` 소스를 감지하면 graph_client로 N-hop 이웃을 탐색하여 rerank 후보에 포함.

### /handoff 하네스 검증

`harness_verifier.verify()` 로 핵심 파일 무결성을 SHA256 해시로 검증. graph_meta.yaml 이 존재하는 프로젝트에서만 실행.
