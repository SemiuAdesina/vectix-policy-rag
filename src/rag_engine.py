"""
RAG engine for VectixLogic policy Q&A.

Orchestrates retrieval, prompting, guardrails, and latency tracking.
"""

import logging
import time
from typing import Any, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from src.rag_helpers import (
    answer_is_unsupported,
    build_display_chunks,
    extract_cited_policy_ids,
    extract_sources,
    rerank_docs,
)

logger = logging.getLogger(__name__)
_latency_ms: List[float] = []

SYSTEM_PROMPT = """You answer questions using ONLY the provided policy context. Use exact terminology from the context (e.g. from Appendix: Definitions). Cite the Policy ID (e.g. VL-SEC-019) when you use a policy. If the context does not contain relevant information, say so and do not invent an answer. Keep answers under 300 words."""


def _latency_tracker(func: Any) -> Any:
    """Decorator: measure request latency (ms) and log; store for p50/p95."""

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return func(self, *args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            _latency_ms.append(elapsed_ms)
            logger.info("rag_request_latency_ms=%.2f", elapsed_ms)

    return wrapper


def get_latency_percentiles() -> dict:
    """Return p50 and p95 of recorded request latencies (ms)."""
    if not _latency_ms:
        return {"p50_ms": None, "p95_ms": None}
    samples = sorted(_latency_ms)
    size = len(samples)
    return {
        "p50_ms": samples[int(0.50 * (size - 1))],
        "p95_ms": samples[int(0.95 * (size - 1))],
    }


class RAGEngine:
    """Retrieval-augmented generation for the VectixLogic policy corpus."""

    def __init__(self, vector_store: Any, llm: Runnable) -> None:
        self._store = vector_store
        self._llm = llm

    @_latency_tracker
    def ask(self, query: str, k: int = 4) -> dict:
        """Retrieve chunks, generate an answer, and return display-ready evidence."""
        docs = self._retrieve_docs(query, k)
        if not docs:
            return {
                "answer": "I have no policy context for that question. Please ask about VectixLogic policies.",
                "sources": [],
                "chunks": [],
            }
        answer = self._generate_answer(query, docs)
        if answer_is_unsupported(answer):
            return {"answer": answer, "sources": [], "chunks": []}
        cited_sources = extract_cited_policy_ids(answer)
        sources = cited_sources or extract_sources(docs, preferred=cited_sources)
        chunks = build_display_chunks(docs, cited_sources=cited_sources, limit=2)
        return {"answer": answer, "sources": sources, "chunks": chunks}

    def _retrieve_docs(self, query: str, k: int) -> list:
        """Fetch more than k docs and rerank before generation."""
        fetch_k = max(k, min(12, k * 3))
        docs = self._store.similarity_search(query, k=fetch_k)
        return rerank_docs(query, docs, k)

    def _generate_answer(self, query: str, docs: list) -> str:
        """Call the LLM with retrieved context and return the answer text."""
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}"),
        ]
        response = self._llm.invoke(messages)
        return getattr(response, "content", str(response))
