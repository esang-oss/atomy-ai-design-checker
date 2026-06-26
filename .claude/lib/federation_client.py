"""Federation readiness 레이어 — 현재 Null stub, 미래 교차 사용자 교차 팔레이스 조회로 채워짐.

본 모듈이 정의하는 Protocol 이 미래 실구현의 계약 (contract). 지금부터 /rpi 가
get_federation_client().search(query) 를 항상 호출하므로, 미래에 factory 만 교체하면
/rpi 코드 변경 없이 교차 회상이 활성화된다.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class FederationSnippet:
    """교차 팔레이스 조회 결과의 단일 스니펫. 미래 실구현이 반환하는 형태."""
    id: str
    source_palace: str       # e.g., "cfo-laptop", "marketing-lead-mac"
    source_user: str         # user_id 식별자
    body: str
    metadata: dict = field(default_factory=dict)


class FederationClient(Protocol):
    """미래 실구현이 만족해야 할 계약.

    [R2] wings·halls 파라미터는 downstream B1 federation-service 가 여러 Spoke
    Palace 에 동일한 Wing/Hall 필터를 적용할 수 있도록 미리 계약에 포함한다.
    Null stub 은 이들을 무시하고 [] 를 반환한다.
    """
    def search(
        self,
        query: str,
        *,
        wings: list[str] | None = None,
        halls: list[str] | None = None,
        top_k: int = 10,
    ) -> list[FederationSnippet]: ...
    def is_available(self) -> bool: ...


class NullFederationClient:
    """현재 기본 구현. 항상 빈 리스트 반환. /rpi 는 이걸 모른 채로 호출만 함."""

    def search(
        self,
        query: str,
        *,
        wings: list[str] | None = None,
        halls: list[str] | None = None,
        top_k: int = 10,
    ) -> list[FederationSnippet]:
        return []

    def is_available(self) -> bool:
        return False


def get_federation_client() -> FederationClient:
    """Factory. 현재는 항상 Null, 미래엔 ~/.claude/federation.json 로드.

    config 파일이 존재하지만 실구현이 아직 없는 경우 경고만 로그하고 Null fallback.
    """
    config_path = os.path.join(os.path.expanduser("~"), ".claude", "federation.json")
    if os.path.exists(config_path):
        print(
            f"WARN: {config_path} exists but federation is not implemented yet. "
            "Falling back to NullFederationClient.",
            file=sys.stderr,
        )
        return NullFederationClient()
    return NullFederationClient()
