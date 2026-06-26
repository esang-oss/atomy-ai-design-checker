"""data_source YAML 파싱 + 실시간 조회 + privacy 확인.

모든 조회 실패는 None 반환 (silent). /rpi 를 블록하지 않는다.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def load_sources(project_root: str) -> list[dict]:
    """graph/sources/ 디렉토리에서 모든 data_source YAML 로드."""
    src_dir = Path(project_root) / ".claude" / "memory" / "graph" / "sources"
    if not src_dir.exists():
        return []
    sources = []
    for yaml_file in sorted(src_dir.glob("*.yaml")):
        content = yaml_file.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        if isinstance(parsed, dict) and parsed.get("id"):
            sources.append(parsed)
    return sources


def find_source(sources: list[dict], source_id: str) -> dict | None:
    """ID로 data_source 조회."""
    for s in sources:
        if s.get("id") == source_id:
            return s
    return None


def check_privacy(source: dict, *, requester_dept: str = "") -> bool:
    """privacy_level 확인."""
    level = source.get("privacy_level", "public")
    if level == "public":
        return True
    if level == "department":
        return source.get("owner_dept", "") == requester_dept
    if level == "restricted":
        return False  # 별도 ACL 필요 — 기본 거부
    return False


def resolve(source: dict, *, timeout: int = 5) -> dict | None:
    """data_source endpoint 실시간 조회. 실패 시 None."""
    src_type = source.get("type", "")
    endpoint = source.get("endpoint", "")
    if not endpoint:
        return None

    # Auth: env: 접두사 → 환경변수에서 키 로드
    auth = source.get("auth", "")
    api_key = None
    if auth.startswith("env:"):
        env_var = auth[4:]
        api_key = os.environ.get(env_var)

    if src_type == "api":
        try:
            req = urllib.request.Request(endpoint)
            if api_key:
                req.add_header("Authorization", f"Bearer {api_key}")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    # database, spreadsheet, dashboard → 미구현 (Phase 2+)
    logger.info("data_source type '%s' not yet implemented", src_type)
    return None
