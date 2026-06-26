"""DEPRECATION SHIM — embedding_provider 의 backend impl 은 examples/embedding/ 으로 이동.

기존 사용처 호환을 위한 re-export. 다음 메이저에서 제거 예정.

backend impl import 는 lazy (PEP 562 __getattr__) — google-genai / chromadb 등
backend 별 의존성이 미설치된 환경에서도 shim 자체는 import 가능.

스펙: docs/specs/2026-05-04-embedding-neutralization.md §4-5
"""
from __future__ import annotations

import importlib
import os
import warnings

# DeprecationWarning은 shim 모듈 import 시 한 번.
warnings.warn(
    ".claude/lib/embedding_provider 는 deprecated. "
    "신규 코드는 `from atomy_toolkit.embedding.factory import get_backend` 또는 "
    "`from examples.embedding.gemini import GeminiEmbedder` 사용.",
    DeprecationWarning,
    stacklevel=2,
)

# ABC + factory 는 toolkit core (의존성 0) — 즉시 import 가능
from atomy_toolkit.embedding.backend import EmbeddingBackend, EmbeddingProvider  # noqa: F401, E402
from atomy_toolkit.embedding.factory import get_backend  # noqa: F401, E402

# 기존 클래스 이름 → 이동 위치 매핑
_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "LocalEmbeddingProvider": ("examples.embedding.local", "LocalEmbedder"),
    "LocalEmbedder": ("examples.embedding.local", "LocalEmbedder"),
    "GeminiEmbeddingProvider": ("examples.embedding.gemini", "GeminiEmbedder"),
    "GeminiEmbedder": ("examples.embedding.gemini", "GeminiEmbedder"),
    "OllamaEmbedder": ("examples.embedding.ollama", "OllamaEmbedder"),
    "VertexEmbedder": ("examples.embedding.vertex", "VertexEmbedder"),
}


def __getattr__(name: str):
    """PEP 562 module-level __getattr__ — backend 클래스 lazy resolution."""
    if name in _LAZY_EXPORTS:
        module_name, class_name = _LAZY_EXPORTS[name]
        return getattr(importlib.import_module(module_name), class_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_provider():
    """Legacy factory — GEMINI_API_KEY 보유 시 Gemini, 아니면 Local."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        cls = __getattr__("GeminiEmbeddingProvider")
        return cls(api_key=api_key)
    cls = __getattr__("LocalEmbeddingProvider")
    return cls()


def get_embedder():
    """Legacy factory — get_backend() wrapper, fallback get_provider()."""
    backend = get_backend()
    if backend is not None:
        return backend
    return get_provider()
