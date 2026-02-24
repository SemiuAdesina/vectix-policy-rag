"""
RAG (Retrieval-Augmented Generation) engine for VectixLogic policy Q&A.

Orchestrates top-k retrieval, prompt guardrails, and LLM generation.
Uses dependency injection for vector store and LLM. Tracks latency for p50/p95.
"""

import logging
import time
from typing import Any, List

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

logger = logging.getLogger(__name__)

# Latency history for p50/p95 (per .cursorrules)
_latency_ms: List[float] = []


def _latency_tracker(func: Any) -> Any:
    """Decorator: measure request latency (ms) and log; store for p50/p95."""
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            out = func(self, *args, **kwargs)
            return out
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            _latency_ms.append(elapsed_ms)
            logger.info("rag_request_latency_ms=%.2f", elapsed_ms)
    return wrapper


def get_latency_percentiles() -> dict:
    """Return p50 and p95 of recorded request latencies (ms)."""
    if not _latency_ms:
        return {"p50_ms": None, "p95_ms": None}
    s = sorted(_latency_ms)
    n = len(s)
    p50 = s[int(0.50 * (n - 1))] if n else None
    p95 = s[int(0.95 * (n - 1))] if n else None
    return {"p50_ms": p50, "p95_ms": p95}


SYSTEM_PROMPT = """You answer questions using ONLY the provided policy context. Use exact terminology from the context (e.g. from Appendix: Definitions). Cite the Policy ID (e.g. VL-SEC-019) when you use a policy. If the context does not contain relevant information, say so and do not invent an answer. Keep answers under 300 words."""


class RAGEngine:
    """
    Retrieval-augmented generation for VectixLogic policy corpus.

    Vector store and LLM are injected (no hardcoded connection). Enforces
    guardrails via system prompt: only use context, exact terminology, refuse out-of-corpus.
    """

    def __init__(self, vector_store: Any, llm: Runnable) -> None:
        """
        Initialize the RAG engine.

        Args:
            vector_store: Must implement similarity_search(query, k).
            llm: LangChain LLM or runnable (invoke with messages).
        """
        self._store = vector_store
        self._llm = llm

    @_latency_tracker
    def ask(self, query: str, k: int = 4) -> dict:
        """
        Retrieve top-k chunks, generate answer with guardrails, return answer and sources.

        Args:
            query: User question.
            k: Number of chunks to retrieve.

        Returns:
            Dict with "answer" (str) and "sources" (list of source identifiers, e.g. Policy ID).
        """
        # Retrieve
        docs = self._store.similarity_search(query, k=k)
        if not docs:
            return {
                "answer": "I have no policy context for that question. Please ask about VectixLogic policies.",
                "sources": [],
                "chunks": [],
            }
        context = "\n\n---\n\n".join(d.page_content for d in docs)
        sources = _extract_sources(docs)
        chunks = [{"content": d.page_content, "source": (d.metadata or {}).get("id") or (d.metadata or {}).get("source") or "—"} for d in docs]
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}"),
        ]
        response = self._llm.invoke(messages)
        answer = getattr(response, "content", str(response))
        return {"answer": answer, "sources": sources, "chunks": chunks}


def _extract_sources(docs: List[Document]) -> List[str]:
    """Extract unique source identifiers (Policy ID or source file) from doc metadata."""
    seen = set()
    out = []
    for d in docs:
        meta = d.metadata or {}
        sid = meta.get("id") or meta.get("source") or meta.get("policy_id")
        if sid and sid not in seen:
            seen.add(sid)
            out.append(str(sid))
    return out
