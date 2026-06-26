"""/rpi 질의 분류기 — ASMR / memtemple / both 결정.

미매칭 기본은 'both' (safer default). 정규식은 한/영 혼용.
[S7] 쿼리 길이 10KB 초과 시 truncate + 경고.

T-v1.x-A.5 (2026-05-20): 라우팅 키 'mempalace' -> 'memtemple' rename.
패턴 자체는 동일 (시간성 키워드 + 대화 회상 키워드), source label 만 갱신.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

MAX_QUERY_BYTES = 10 * 1024  # 10 KB (S7)

_ASMR_PATTERNS = [
    re.compile(r"\b왜\b", re.UNICODE),
    re.compile(r"이유", re.UNICODE),
    re.compile(r"근거", re.UNICODE),
    re.compile(r"어떤\s*이유", re.UNICODE),
    re.compile(r"\bwhy\b", re.IGNORECASE),
    re.compile(r"\bbecause\b", re.IGNORECASE),
    re.compile(r"\brationale\b", re.IGNORECASE),
]

_MEMTEMPLE_PATTERNS = [
    re.compile(r"지난주|지난달|지난\s*\d+", re.UNICODE),
    re.compile(r"과거|예전|이전에", re.UNICODE),
    re.compile(r"이야기|논의|말했|말한\s*적", re.UNICODE),
    re.compile(r"\blast\s+(week|month|year)\b", re.IGNORECASE),
    re.compile(r"\bpreviously\b", re.IGNORECASE),
    re.compile(r"\b\d+\s+(days?|weeks?|months?)\s+ago\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+did\s+we\b", re.IGNORECASE),
]

_GRAPH_PATTERNS = [
    re.compile(r"관련된|연결된|연관|관계", re.UNICODE),
    re.compile(r"용어|정의|뜻|의미", re.UNICODE),
    re.compile(r"\brelated\s+to\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+is\b", re.IGNORECASE),
    re.compile(r"\bdepend", re.IGNORECASE),
    re.compile(r"\bglossary\b", re.IGNORECASE),
]

_TRUNCATE_WARNED = False


@dataclass
class RoutingDecision:
    """질의 분류 결과. sources 는 'asmr' / 'memtemple' 포함 가능한 set."""
    query: str
    sources: set[str] = field(default_factory=set)
    matched_patterns: list[str] = field(default_factory=list)


def _truncate_if_oversized(query: str) -> str:
    """[S7] 10KB 초과 시 truncate + 1회 경고."""
    global _TRUNCATE_WARNED
    encoded = query.encode("utf-8")
    if len(encoded) <= MAX_QUERY_BYTES:
        return query
    # Truncate at byte boundary, safely decode
    truncated_bytes = encoded[:MAX_QUERY_BYTES]
    try:
        truncated = truncated_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # Drop trailing bytes until valid decode
        for i in range(1, 5):
            try:
                truncated = truncated_bytes[:-i].decode("utf-8")
                break
            except UnicodeDecodeError:
                continue
        else:
            truncated = ""
    if not _TRUNCATE_WARNED:
        logger.warning(
            "router: query exceeded %d bytes (was %d); truncated",
            MAX_QUERY_BYTES, len(encoded),
        )
        _TRUNCATE_WARNED = True
    return truncated


def classify(query: str) -> RoutingDecision:
    """질의를 ASMR, mempalace, 또는 둘 다로 분류."""
    query = _truncate_if_oversized(query)
    decision = RoutingDecision(query=query)

    for pat in _ASMR_PATTERNS:
        if pat.search(query):
            decision.sources.add("asmr")
            decision.matched_patterns.append(pat.pattern)
            break

    for pat in _MEMTEMPLE_PATTERNS:
        if pat.search(query):
            decision.sources.add("memtemple")
            decision.matched_patterns.append(pat.pattern)
            break

    for pat in _GRAPH_PATTERNS:
        if pat.search(query):
            decision.sources.add("graph")
            decision.matched_patterns.append(pat.pattern)
            break

    if not decision.sources:
        decision.sources = {"asmr", "memtemple"}

    return decision
