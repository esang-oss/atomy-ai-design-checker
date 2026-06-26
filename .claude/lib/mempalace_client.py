"""memtemple 위의 얇은 shim — MemorySnippet schema 유지 + bm25 검색 위임.

T-v1.x-A.5 이전: 이 모듈은 `mempalace` CLI 를 subprocess 로 호출하고 chromadb
librarian 으로 fallback 하는 437 LOC 의 두꺼운 wrapper 였다. T-v1.x-A.4 에서
handoff 의 mine() 호출이 `atomy-toolkit memtemple save` 로 치환되면서 mine 경로는
이미 폐기됐고, T-v1.x-A.5 (본 모듈) 가 search 경로까지 memtemple 로 옮긴다.

남는 책임:
  1. `MemorySnippet` dataclass schema 유지 — rerank/router/graph_client/
     palace_librarian 4 파일이 import 중이라 shape 변경 시 회귀.
  2. `search(query, wings=..., top_k=...)` — memtemple `bm25_search` 위로 래핑.
  3. `is_available()` — memtemple vault 존재 여부 검사 (semantics 변경).

삭제된 책임 (T-v1.x-A.5):
  - mempalace CLI subprocess 호출 (`mempalace search`, `mempalace mine`)
  - chromadb librarian 우선 경로
  - JSONL -> md 변환 (`atomy_toolkit.memtemple.plugins.claude_code.extractor` 가 대체)
  - 세션 로그 경로 추론 (`atomy_toolkit.memtemple.core.session_locator.find_session_log()` 가 대체)
  - ASMR backfill (deprecated)
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public schema — shape contract for rerank/router/graph_client/palace_librarian
# ---------------------------------------------------------------------------

@dataclass
class MemorySnippet:
    """memtemple (또는 future ASMR/graph) 에서 온 단일 메모리 스니펫.

    Shape contract: 4 필드, 이름·순서 변경 금지. T-v1.x-A.5 이전 mempalace 검색
    결과와 호환되도록 source 값만 "mempalace" -> "memtemple" 로 의미 갱신.
    """
    id: str
    source: str  # "memtemple" | "asmr" | "graph"
    body: str
    metadata: dict[str, Any]


# ---------------------------------------------------------------------------
# Public API — search 와 availability
# ---------------------------------------------------------------------------

def get_palace_home() -> str:
    """Vault root 경로 반환. MEMTEMPLE_HOME 우선, 없으면 ~/.memtemple/.

    Naming: 함수 이름은 호환성을 위해 `get_palace_home` 유지 (rerank/router 가
    아직 의존). 반환값의 의미는 T-v1.x-A.5 부터 memtemple vault.
    """
    env = os.environ.get("MEMTEMPLE_HOME") or os.environ.get("MEMPALACE_HOME")
    if env:
        return env
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME")
    if not home:
        return os.path.expanduser("~/.memtemple")
    return os.path.join(home, ".memtemple")


def is_available() -> bool:
    """memtemple vault 가 존재하는지 검사. v1.x-A.5 부터 CLI 검사가 아니라
    vault root 디스크 점검 (`<root>/.memtemple_version` 존재 여부)."""
    root = Path(get_palace_home())
    stamp = root / ".memtemple_version"
    return root.is_dir() and stamp.is_file()


def search(
    query: str,
    *,
    wings: list[str] | None = None,
    halls: list[str] | None = None,
    top_k: int = 10,
) -> list[MemorySnippet]:
    """memtemple vault 위 BM25 검색. 모든 실패는 빈 리스트로 silent fallback.

    wings: 검색할 wing 이름 list. None 이면 vault root 전체 (cross-wing).
    halls: deprecated noop (mempalace metadata 의 hall 필드 잔재) — 시그니처
           호환성 위해 유지, 값 무시.
    top_k: 반환할 최대 결과 수.
    """
    try:
        from atomy_toolkit.memtemple.core.search import bm25_search
    except Exception:
        return []

    root = Path(get_palace_home())
    if not root.is_dir():
        return []

    if wings:
        wing_roots = [root / w for w in wings if (root / w).is_dir()]
    else:
        wing_roots = [
            p for p in root.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        ]

    aggregated: list[tuple[float, MemorySnippet]] = []
    for wing_root in wing_roots:
        try:
            results = bm25_search(wing_root, query, top_k=top_k)
        except Exception:
            continue
        for r in results:
            snippet = MemorySnippet(
                id=r.path.stem,
                source="memtemple",
                body=_drawer_body_excerpt(r.path),
                metadata={
                    "wing": wing_root.name,
                    "room": r.path.parent.name,
                    "score": str(r.score),
                    "source_file": str(r.path),
                },
            )
            aggregated.append((r.score, snippet))

    aggregated.sort(key=lambda x: -x[0])
    return [s for _, s in aggregated[:top_k]]


def _drawer_body_excerpt(path: Path, max_chars: int = 500) -> str:
    """Drawer body (frontmatter 제외) 의 앞부분 발췌. 본문 파싱 실패 시 빈 문자열."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    parts = text.split("---", 2)
    body = parts[2].strip() if len(parts) >= 3 else text.strip()
    return body[:max_chars]
