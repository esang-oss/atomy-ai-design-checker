# =============================================================================
# TRUST BOUNDARY (Rev 2.1 Security S8)
# =============================================================================
# This module directly accesses mempalace's internal ChromaDB collection layout.
# Phase 1 assumptions (single-user, local, trusted filesystem) are REQUIRED —
# in a multi-user environment, any user could invoke this module to tamper with
# another user's drawer metadata. Multi-user deployments MUST use Phase 2 B4's
# native metadata API instead of this patcher.
#
# palace_path is validated at runtime to be a subpath of MEMPALACE_HOME (or the
# default ~/.mempalace), preventing trivial path-confusion attacks within the
# single-user trust model. This is NOT sufficient for multi-user isolation.
#
# Removal plan: Phase 2 B4 will provide native metadata_tags at mine() time,
# eliminating the need for post-patching entirely. This file is expected to be
# deleted at that point.
# =============================================================================
"""ChromaDB metadata patcher — Q9 option D post-mine metadata injection.

[R2.2] Trust boundary: Phase 1 assumes single-user, local ChromaDB. This module
directly accesses mempalace's internal ChromaDB collection `mempalace_drawers`
and is removed in Phase 2 when B4 provides native metadata API.

Day 1 tagging of user_id/department_id/org_id enables Phase 2 B4 transition
by metadata query (re-indexing unnecessary).
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# [R2.2] Immutable required metadata keys. Day 1 tagging enables Phase 2 re-classification.
REQUIRED_METADATA_KEYS: frozenset[str] = frozenset({
    "user_id",
    "department_id",
    "org_id",
    "project_id",
    "palace_version",
    "session_timestamp",
})


def resolve_identity_metadata() -> dict[str, str]:
    """Resolve user/department/org identifiers via env var priority.

    MEMPALACE_USER_ID > "local"
    MEMPALACE_DEPARTMENT_ID > "default"
    MEMPALACE_ORG_ID > "default"
    """
    return {
        "user_id": os.environ.get("MEMPALACE_USER_ID") or "local",
        "department_id": os.environ.get("MEMPALACE_DEPARTMENT_ID") or "default",
        "org_id": os.environ.get("MEMPALACE_ORG_ID") or "default",
    }


@dataclass
class PatchResult:
    ok: bool
    patched: int = 0
    error: str | None = None


def is_patcher_available() -> bool:
    """chromadb 패키지 import 가능 여부 확인 (palace 경로 존재는 호출자 책임)."""
    try:
        import chromadb  # noqa: F401
        return True
    except ImportError:
        return False


def _age_seconds(filed_at: str | float, now: float) -> float:
    """filed_at (ISO8601 string or unix timestamp) 와 now 의 차이를 초로 반환."""
    if isinstance(filed_at, (int, float)):
        return now - float(filed_at)
    # ISO8601 string
    from datetime import datetime
    try:
        # Accept 'Z' suffix
        s = filed_at.rstrip("Z") if filed_at.endswith("Z") else filed_at
        dt = datetime.fromisoformat(s)
        return now - dt.timestamp()
    except (ValueError, AttributeError):
        return float("inf")  # unparseable → treat as very old


def patch_recent_drawers(
    palace_path: str,
    source_file_marker: str,
    federation_metadata: dict[str, str],
    *,
    max_age_seconds: float = 60.0,
    canonical_source: str | None = None,
) -> PatchResult:
    """mine 직후 호출. source_file 이 marker 와 일치하고 filed_at 이 최근 max_age_seconds
    내인 drawer 를 찾아 metadata 를 병합 업데이트.

    federation_metadata 는 REQUIRED_METADATA_KEYS 의 부분집합이 아니면 ValueError.
    호출자는 resolve_identity_metadata() 결과를 baseline 으로 병합해서 전달한다.

    canonical_source 가 주어지면 매칭된 drawer 의 source_file 메타를 해당 값으로
    덮어쓴다. mempalace CLI 가 tempdir 경로를 source_file 로 저장하는 문제를
    사후 교정하는 용도 — 재-mine 시 동일 원본이 동일 ID 로 매핑되도록 보장.

    ChromaDB 단일 컬렉션 `mempalace_drawers` (upstream 기본값) 가정. 실패 시
    PatchResult(ok=False). 실패해도 mine() 전체는 성공 유지 (drawer 는 이미 저장됨).
    """
    # Validate metadata keys
    missing = REQUIRED_METADATA_KEYS - federation_metadata.keys()
    if missing:
        raise ValueError(
            f"federation_metadata missing required keys: {sorted(missing)}. "
            f"Caller must merge resolve_identity_metadata() as baseline."
        )

    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        return PatchResult(ok=False, error="chromadb package not installed")

    # [S8] palace_path must be canonical subpath of MEMPALACE_HOME or ~/.mempalace.
    # Runs only if chromadb is present so chromadb-absent callers get the original error first.
    try:
        canonical_palace = os.path.realpath(palace_path)
        trusted_root_raw = os.environ.get("MEMPALACE_HOME") or os.path.expanduser("~/.mempalace")
        trusted_root = os.path.realpath(trusted_root_raw)
        sep = os.sep
        if canonical_palace != trusted_root and not canonical_palace.startswith(trusted_root + sep):
            return PatchResult(
                ok=False,
                error=f"palace_path outside trusted root ({trusted_root})",
            )
    except Exception as exc:
        return PatchResult(ok=False, error=f"palace_path validation failed: {exc}")

    try:
        client = chromadb.PersistentClient(
            path=palace_path,
            settings=Settings(anonymized_telemetry=False),
        )
    except Exception as e:
        return PatchResult(ok=False, error=f"chromadb open failed: {e}")

    patched_total = 0
    try:
        collections = client.list_collections()
    except Exception as e:
        return PatchResult(ok=False, error=f"list_collections failed: {e}")

    now = time.time()
    for coll in collections:
        try:
            results = coll.get(where={"source_file": source_file_marker})
        except Exception:
            continue
        if not results or not results.get("ids"):
            continue

        new_metas: list[dict[str, str]] = []
        new_ids: list[str] = []
        ids = results["ids"]
        metadatas = results.get("metadatas") or []
        for drawer_id, meta in zip(ids, metadatas):
            if not isinstance(meta, dict):
                continue
            filed_at = meta.get("filed_at")
            if filed_at is None:
                continue
            if _age_seconds(filed_at, now) > max_age_seconds:
                continue
            merged = {**meta, **federation_metadata}
            if canonical_source is not None:
                merged["source_file"] = canonical_source
            new_metas.append(merged)
            new_ids.append(drawer_id)

        if new_ids:
            try:
                coll.update(ids=new_ids, metadatas=new_metas)
                patched_total += len(new_ids)
            except Exception as e:
                logger.warning("coll.update failed: %s", e)

    return PatchResult(ok=True, patched=patched_total)
