# 코드 리뷰

다음 파일 또는 변경사항을 리뷰해주세요: $ARGUMENTS

## Step 0: dispatcher verifying 게이트 (해당 시)

codex 가 `/implement` 로 위임한 work-order 가 `verifying` 에 있으면, 일반 리뷰 대신 이 게이트를 수행한다.

```python
import sys; sys.path.insert(0, '.')
from pathlib import Path
from atomy_toolkit.dispatcher.state import load_state
state = load_state(Path('.atomy/dispatcher-state.yaml'))
gate = bool(state and state.work_order.state == 'verifying')
print('GATE' if gate else 'NO_GATE — 아래 일반 코드 리뷰로 진행')
if gate:
    wo = state.work_order
    r = wo.result or {}
    print('wo.id =', wo.id)
    print('files_changed:', r.get('files_changed', []))
    print('tests:', r.get('tests', {}))
    print('reconcile:', r.get('reconcile', {}))
```

게이트일 때:

1. **diff 제시** — `wo.result['files_changed']` 경로만 스코프해서 본다 (전체 worktree 금지 — dirty
   worktree 의 무관한 사람 변경 혼입 방지). 그 파일들의 변경을 읽어 파악한다 (`git diff -- <그 파일들>`).
   `files_changed` 가 비면 "변경 없음 — reconcile 확인" 을 제시.
2. **평가** — 아래 "## 일반 코드 리뷰" 의 전 항목으로 codex diff 를 평가하고 approve/revise/reject 를
   **추천** + 근거를 제시한다.
3. **사람이 결정** — 이 게이트는 워크플로 *컨벤션*이다. CLI 는 호출자가 사람인지 모델인지 구분하지
   못하므로, **반드시 사람의 결정을 받은 뒤** 아래를 호출한다 (Claude 자율 승인 금지).

```python
from atomy_toolkit.dispatcher.cli import main
from atomy_toolkit.dispatcher import implement
# 사람 결정에 따라 정확히 하나만:
# --- approve ---
main(['approve', '--atomy-dir', '.atomy'])                 # verifying -> done (전이만)
n = implement.mark_task_complete('docs/plans', wo.id)      # plan 체크박스 (전이와 별개; 실패해도 전이 보존)
print(f'plan 체크박스 {n}개 갱신' if n else 'plan 미발견/해당없음 — 수동 확인')
slug = implement.parse_wo_id(wo.id)                         # plan 봉인 (모든 box [x] 일 때만 헤더 마커 stamp)
sealed = implement.seal_plan_if_complete('docs/plans', slug[0]) if slug else False
print('plan 봉인(**Status:** shipped)' if sealed else 'plan 미완/이미봉인 — 봉인 안 함')
# --- revise ---  (수정 instructions 로 재드라이브는 후속 /implement 가 ready->resume 으로 담당)
# main(['revise', '--atomy-dir', '.atomy'])
# --- reject ---
# main(['reject', '--atomy-dir', '.atomy'])
main(['status', '--atomy-dir', '.atomy'])                  # 결과 보고
```

verifying WO 가 없으면(NO_GATE) 아래 일반 코드 리뷰를 그대로 진행한다.

---

## 일반 코드 리뷰

### 1. 보안 점검
- `.claude/skills/security-check/SKILL.md`의 전체 체크리스트 기준으로 점검
- 특히: API 키 하드코딩, SSRF, XSS, 파일 업로드 보안, 에러 마스킹

### 2. 에러 처리
- 외부 API 호출에 try-except/try-catch가 있는가
- **빈 catch 블록**(`catch { return null }`)이 없는가 — Silent Failure 금지
- 에러 발생 시 적절한 로그를 남기는가 (logger.error)
- 프로덕션 에러 응답에 스택트레이스가 노출되지 않는가 (에러 마스킹)

### 3. 코드 품질
- 중복 코드가 있는가
- **200줄 이상**인 함수가 있는가 (분리 필수)
- 50줄 이상인 함수가 있는가 (분리 권장)
- 변수/함수명이 역할을 명확히 설명하는가
- **매직 넘버** 대신 중앙 상수 파일(`config/constants`)을 사용하는가

### 4. 타입 안전성 (TypeScript)
- `any` 타입이 사용되었는가 → `unknown` + 타입 가드로 대체 필요
- `parseInt()` 호출에 기수(radix)가 명시되어 있는가
- Non-null assertion(`!`)이 남용되었는가

### 5. 비동기/성능
- 반복문 안에서 개별 API/DB 호출이 있는가 (N+1 쿼리 패턴)
- `Promise.all()` 사용 시 동시성 제한이 설정되어 있는가
- DB JSON 컬럼의 이중 인코딩/디코딩이 없는가

### 6. 환경변수/설정
- `|| 'http://localhost:...'` 같은 하드코딩 폴백이 있는가
- 필수 환경변수의 시작 시 검증(`validateEnv`)이 되어 있는가
- 도메인 상수가 Single Source of Truth 파일에서 관리되는가

### 7. 데이터 정합성
- 타입 불일치 가능성이 있는가
- 범위(range) 초과 가능성이 있는가
- None/Null 처리가 되어 있는가

## 보고 형식

발견된 문제를 심각도별로 분류해서 알려주세요:
- 🔴 높음: 즉시 수정 필요 (보안, 데이터 손실, 프로덕션 장애 위험)
- 🟡 중간: 가능한 빨리 수정 (에러 처리 누락, 성능 문제, 타입 안전성)
- 🟢 낮음: 개선 권장 (코드 스타일, 가독성, 매직 넘버)

각 항목에 **파일명:라인번호**와 **수정 제안 코드**를 포함하세요.
