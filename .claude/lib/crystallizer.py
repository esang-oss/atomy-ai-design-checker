"""Phase 4 outcome_window 결정화 (현재 미활성 — handoff wiring 후속 spec 에서).

[D-008 deferred 명시, 2026-05-04 Phase 2 Task 1] — audit P3 (F-002/F-007/F-010)
가 본 모듈을 dead 로 확정. `/handoff` 의 STEP 2.8-F wiring + bootstrap.sh /
upgrade.sh 화이트리스트 등록은 Phase 4 outcome_window 실 데이터 전환 시 별
spec 에서 처리. 본 모듈은 현 시점 호출처 0 — 유지 사유는 미래 옵션 보존.

— 이전 docstring 보존 (Phase 3 T6 shortform-studio Crystallizer 스텁) —
`/handoff` STEP 2.8-F 가 workflow_runs 의 `crystallize_candidate=True` NodeExecution 을
스캔 후 본 함수를 호출하여 Knowledge Fabric capture 를 mempalace drawer 로 결정화한다.
prior spec `2026-04-14-p2-dag-orchestrator-design.md` D11=B (필수 의존성, 명시적 fail-fast).
P4 활성 시점에 본 함수가 실제 결정화 로직 구현으로 교체 (별 spec).
shortform-studio 외 다른 프로젝트도 같은 lib 를 공유 — 각 프로젝트의 P4 활성 여부는
별도 환경변수 (`CRYSTALLIZER_ENABLED=1`) 로 제어 (T7 OSMU 시점에 활성).
"""
from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger(__name__)


def crystallize(*, workflow_run_id: int, **kwargs: Any) -> dict[str, Any]:
    """workflow_run 의 crystallize_candidate=True 노드를 mempalace drawer 로 결정화.

    Args:
        workflow_run_id: v2 WorkflowRun.id

    Returns:
        {"workflow_run_id": ..., "crystallized_count": ..., "drawer_ids": [...]}.

    Raises:
        NotImplementedError: P4 (outcome_window) 미활성 시 (default — Phase 3 ~ Phase 5 까지).
            환경 변수 `CRYSTALLIZER_ENABLED=1` 설정 후 실 구현으로 교체 시 활성화.
    """
    if os.getenv("CRYSTALLIZER_ENABLED", "").strip().lower() not in {"1", "true", "yes"}:
        raise NotImplementedError(
            f"Crystallizer 는 Phase 4 outcome_window 실 데이터 전환 후 활성 "
            f"(prior spec D11=B). workflow_run_id={workflow_run_id}. "
            f"활성화 시 CRYSTALLIZER_ENABLED=1 환경변수 설정 + 본 모듈 실 구현으로 교체."
        )

    # P4 도래 시 본 영역에 실 구현 (별 spec). 현재 placeholder.
    log.info(
        "Crystallizer 활성 (CRYSTALLIZER_ENABLED=1) — workflow_run_id=%s placeholder 결과 반환",
        workflow_run_id,
    )
    return {
        "workflow_run_id": workflow_run_id,
        "crystallized_count": 0,
        "drawer_ids": [],
    }


__all__ = ["crystallize"]
