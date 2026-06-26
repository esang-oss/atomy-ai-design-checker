# /implement — approved plan 의 다음 Task 를 codex 에 위임

`/implement [hint]` — dispatcher 척추(S1~S3) 위에 얹힌 진입점. approved plan 의 다음
미체크 Task 를 골라 codex 에 위임하고, FSM 을 verifying/blocked/failed 까지 구동한 뒤
사람 리뷰로 인계한다. **정책은 `implement.py` 헬퍼가, codex 프롬프트는 너(Claude)가 작성한다.**

> Zero-Allowance: 이 doc 은 shell 명령을 지시하지 않는다. dispatcher 가 codex 를
> subprocess 로 띄우는 것은 아래 python 호출 *내부*에서 일어나는 documented opt-out 이다.
> 모든 코드는 python-level 내부 import 호출로 실행한다 (NF-M6: powershell/bash fence 금지).

## Background worker orchestration (Slice 2)

Non-blocking `/implement` uses the queue coordinator and a background worker:

1. Select the next task, compute `compute_task_sha(sel.task_block)`, and enqueue a `QueueEntry`.
2. If `should_spawn_next(queue.status(...))` is true (`depth > 0`, `active is None`, `halted is False`), spawn an Agent with `run_in_background: true`.
3. The background Agent runs `python -m atomy_toolkit.dispatcher.worker run-one --worker-id <id> --plans-dir docs/plans --atomy-dir .atomy`.
4. When the WorkerReport returns, the main session reviews the diff/evidence path and decides the commit. The worker never commits.
5. After completion, spawn the next worker only when `depth > 0`, `active is None`, and `halted is False`.
6. `/implement tick` may run the same `should_spawn_next` check to advance a queued item after a missed notification or a completed active lease.

## Step 1: Task 선택 (결정적)

```python
import sys; sys.path.insert(0, '.')
from atomy_toolkit.dispatcher import implement
try:
    sel = implement.select_task('docs/plans', hint=None)  # hint = /implement 인자 (있으면)
except implement.NoTaskError as e:
    print(f'NO_TASK: {e}')   # → Step 5 의 NO_TASK 안내
    raise SystemExit
print(f'plan={sel.plan_path.name} task#{sel.task_number} wo_id={sel.wo_id}')
print(sel.task_block)
```

선택된 plan/Task 를 사용자에게 1줄로 보고한다 (어느 plan 의 몇 번 Task 인지 — 투명성).

## Step 2: 현재 state 로 동작 결정 (결정적)

```python
from pathlib import Path
from atomy_toolkit.dispatcher.state import load_state
state = load_state(Path('.atomy/dispatcher-state.yaml'))
act = implement.decide_action(state, sel, force=False)  # force=True 는 사용자 명시 시만
print(f'verb={act.verb} reason={act.reason}')
print('calls=', act.calls)
```

`act.verb == 'refuse'` 이면 `act.reason` 을 사용자에게 출력하고 **정지**한다
(executing stranded → `abandon` 후 재실행 안내 / verifying → `/review` 안내).

## Step 3: codex instructions 작성 (너가 단독 작성)

`sel.task_block` + 관련 spec(`docs/specs/`)·AC 맥락을 읽고, **self-contained codex
프롬프트**를 작성한다. 반드시 포함: 대상 파일 경로, 무엇을 구현·수정할지, 관련 AC 번호,
검증 명령(테스트/빌드). codex 는 그 프롬프트만으로 독립 실행되므로 외부 참조 없이 완결적이어야 한다.

`act.verb == 'answer_then_resume'` (blocked 복구)면 instructions = **codex 질문에 대한 답변**
이다 (`status` 로 질문 확인 후 작성).

**Plan bookkeeping (경로구분):** codex 가 dispatcher 경유(본 `/implement`)로 실행되면 plan 체크박스
flip 은 `/review` approve 게이트의 `mark_task_complete`+`seal_plan_if_complete` 가 담당한다 — codex
프롬프트에 "체크박스를 직접 flip 하거나 `**Status:**` 를 직접 적지 말 것" 을 명시한다(사람 리뷰 보존,
Step 5 정합). codex 가 **dispatcher 밖**에서 자유 실행될 때만(별도 프롬프트) "구현·검증·commit 후 해당
Task 체크박스 flip" 의무를 둔다.

## Step 4: 구동 (S2b CLI 재사용)

```python
from atomy_toolkit.dispatcher.cli import main
instr = """<위에서 너가 작성한 codex 프롬프트 문자열>"""
calls = list(act.calls)
for i, call in enumerate(calls):
    argv = list(call)
    if i == len(calls) - 1 and act.instructions_required:
        argv += ['--instructions', instr]   # 마지막 call 에만 instructions
    rc = main(argv)
    print(f'call {argv[0]} -> rc={rc}')
main(['status', '--atomy-dir', '.atomy'])   # 최종 상태 보고
```

## Step 5: 결과 보고 + 사람 인계

- **verifying** → "codex 구현 완료, 사람 리뷰 필요. `/review` 또는 수동 검토 후 done."
  **너는 verifying→done 을 절대 적용하지 않고 plan 체크박스도 자동 체크하지 않는다** (사람 리뷰 보존).
- **blocked** → codex 질문을 출력, "답변 후 다시 `/implement`" 안내.
- **failed** → `status` 출력으로 사유 표면화, 재시도/조사 안내.
- **NO_TASK** (Step 1) → "실행할 approved plan Task 가 없습니다 — `/rpi` 로 plan 먼저 작성/승인하세요."
