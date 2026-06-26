"""PalaceLibrarian — fast_reject + quality scoring + ingest/search/purge for MemPalace."""
from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone

from embedding_provider import EmbeddingProvider
from google import genai
from mempalace_client import MemorySnippet

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------

BOILERPLATE_MARKERS = [
    "<system-reminder>",
    "<command-name>",
    "<command-message>",
    "Base directory for this skill:",
    "Community mode shares usage data",
    "# RPI 워크플로",
    "AUTO-GENERATED from SKILL.md.tmpl",
]

TEMPDIR_SOURCE_MARKERS = [
    "mempalace_mine_",
]


def fast_reject(text: str, source_file: str = "") -> bool:
    """Return True if *text* or *source_file* matches a reject rule.

    Rejects chunks whose body contains boilerplate markers OR whose source
    originates from an ephemeral mining tempdir (re-mined JSONL session logs).
    """
    for marker in BOILERPLATE_MARKERS:
        if marker in text:
            return True
    for marker in TEMPDIR_SOURCE_MARKERS:
        if marker in source_file:
            return True
    return False


QUALITY_THRESHOLD = 0.3


@dataclass
class Chunk:
    """A single text chunk destined for the librarian."""

    text: str
    source_file: str
    chunk_index: int


LIBRARIAN_COLLECTION = "librarian_drawers"

# ---------------------------------------------------------------------------
# Scoring prompt
# ---------------------------------------------------------------------------

_SCORING_PROMPT = """\
이 텍스트가 프로젝트 고유 지식인지 판별하세요.

점수 기준:
- 0.8~1.0: 설계 결정, 아키텍처 선택, 버그 원인 분석
- 0.5~0.7: 구현 내역, 변경사항 목록, 완료/미완료 항목
- 0.2~0.4: 일반적인 대화, 질문/답변
- 0.0~0.1: 시스템 프롬프트, 워크플로 템플릿, 보일러플레이트, 도구 설명

JSON으로 응답: {"score": 0.7, "reason": "이유"}

텍스트:
"""


# ---------------------------------------------------------------------------
# PalaceLibrarian
# ---------------------------------------------------------------------------


class PalaceLibrarian:
    """Quality-gated ingest, semantic search, and wing purge for the MemPalace."""

    def __init__(self, provider: EmbeddingProvider, palace_home: str) -> None:
        self._provider = provider
        self._palace_home = palace_home
        self._chroma_client = None

        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            self._scorer_client = genai.Client(api_key=api_key)
        else:
            self._scorer_client = None

    # -- scoring ----------------------------------------------------------

    def score_chunk(self, text: str) -> float:
        """Score *text* for project-specific knowledge (0.0..1.0).

        Returns 1.0 pass-through when no Gemini API key is available (intentional
        LocalEmbeddingProvider bypass). On API failure returns 0.0 (fail-closed)
        to avoid flooding the librarian with unverified chunks during rate-limits
        or outages.
        """
        if self._scorer_client is None:
            return 1.0

        try:
            response = self._scorer_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=_SCORING_PROMPT + text,
                config={"response_mime_type": "application/json"},
            )
            data = json.loads(response.text)
            return float(data.get("score", 0.0))
        except Exception:
            logger.warning("score_chunk failed — fail-closed (returning 0.0)", exc_info=True)
            return 0.0

    # -- ChromaDB access --------------------------------------------------

    def _get_collection(self):
        import chromadb

        if self._chroma_client is None:
            self._chroma_client = chromadb.PersistentClient(
                path=os.path.join(self._palace_home, "palace"),
            )
        return self._chroma_client.get_or_create_collection(
            LIBRARIAN_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    # -- ingest -----------------------------------------------------------

    def ingest(self, chunks: list[Chunk], wing: str, room: str) -> int:
        """Ingest *chunks* after fast_reject + quality scoring + body dedup.

        Returns the number of chunks actually stored.
        """
        # Phase 1 & 2: filter + score + dedup (hash-based, per-call)
        passed: list[tuple[Chunk, float]] = []
        seen_body_hashes: set[str] = set()
        for chunk in chunks:
            if fast_reject(chunk.text, chunk.source_file):
                continue
            body_hash = hashlib.sha256(chunk.text.encode("utf-8")).hexdigest()
            if body_hash in seen_body_hashes:
                continue
            seen_body_hashes.add(body_hash)
            score = self.score_chunk(chunk.text)
            if score < QUALITY_THRESHOLD:
                continue
            passed.append((chunk, score))

        if not passed:
            return 0

        # Phase 3: embed
        texts = [c.text for c, _ in passed]
        embeddings = self._provider.embed_documents(texts)

        # Phase 4: upsert
        collection = self._get_collection()
        ids: list[str] = []
        metadatas: list[dict] = []
        documents: list[str] = []

        now_iso = datetime.now(timezone.utc).isoformat()

        for (chunk, score), embedding in zip(passed, embeddings):
            raw = f"{wing}_{room}_{chunk.source_file}_{chunk.chunk_index}"
            doc_id = "lib_" + hashlib.sha256(raw.encode()).hexdigest()[:24]
            ids.append(doc_id)
            documents.append(chunk.text)
            metadatas.append({
                "wing": wing,
                "room": room,
                "source_file": chunk.source_file,
                "chunk_index": chunk.chunk_index,
                "quality_score": score,
                "provider": type(self._provider).__name__,
                "filed_at": now_iso,
            })

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        return len(ids)

    # -- search -----------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        wings: list[str] | None = None,
    ) -> list[MemorySnippet]:
        """Semantic search over ingested chunks."""
        query_embedding = self._provider.embed_query(query)

        where = None
        if wings is not None:
            if len(wings) == 1:
                where = {"wing": wings[0]}
            elif len(wings) > 1:
                where = {"wing": {"$in": wings}}

        collection = self._get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        snippets: list[MemorySnippet] = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return snippets

        for i, doc_id in enumerate(results["ids"][0]):
            doc = results["documents"][0][i] if results.get("documents") else ""
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            distance = results["distances"][0][i] if results.get("distances") else 0.0

            snippets.append(
                MemorySnippet(
                    id=doc_id,
                    source="librarian",
                    body=doc or "",
                    metadata={
                        "wing": meta.get("wing", ""),
                        "room": meta.get("room", ""),
                        "score": 1.0 - distance,
                        "source_file": meta.get("source_file", ""),
                    },
                )
            )
        return snippets

    # -- purge ------------------------------------------------------------

    def purge_wing(self, wing: str) -> int:
        """Delete all documents belonging to *wing*. Return count deleted."""
        collection = self._get_collection()
        results = collection.get(where={"wing": wing}, include=[])
        if not results or not results.get("ids"):
            return 0
        ids = results["ids"]
        if not ids:
            return 0
        collection.delete(ids=ids)
        return len(ids)

    # -- reindex ----------------------------------------------------------

    def reindex_all(self) -> int:
        """Re-ingest from old 'mempalace_drawers' collection through quality filter."""
        import chromadb

        client = chromadb.PersistentClient(
            path=os.path.join(self._palace_home, "palace"),
        )

        try:
            old_collection = client.get_collection("mempalace_drawers")
        except Exception:
            logger.info("No 'mempalace_drawers' collection found; nothing to reindex.")
            return 0

        all_docs = old_collection.get(include=["documents", "metadatas"])
        if not all_docs or not all_docs.get("ids"):
            return 0

        # Group by wing → list of (chunk, room) tuples
        wing_chunks: dict[str, list[tuple[Chunk, str]]] = {}
        for i, doc_id in enumerate(all_docs["ids"]):
            meta = all_docs["metadatas"][i] if all_docs.get("metadatas") else {}
            doc = all_docs["documents"][i] if all_docs.get("documents") else ""
            wing = meta.get("wing", "unknown")
            room = meta.get("room", "unknown")
            source_file = meta.get("source_file", doc_id)
            chunk_index = meta.get("chunk_index", i)

            chunk = Chunk(text=doc or "", source_file=source_file, chunk_index=chunk_index)
            wing_chunks.setdefault(wing, []).append((chunk, room))

        total = 0
        for wing, items in wing_chunks.items():
            # Group by room within wing
            room_chunks: dict[str, list[Chunk]] = {}
            for chunk, room in items:
                room_chunks.setdefault(room, []).append(chunk)

            for room, chunks in room_chunks.items():
                total += self.ingest(chunks, wing=wing, room=room)

        return total
