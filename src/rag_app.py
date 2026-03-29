"""
Application wiring for the policy RAG app.

Builds a RAG engine from environment configuration and falls back to
mock components when no API key is configured.
"""

import os
from typing import Any

from langchain_core.messages import AIMessage

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _mock_embeddings() -> Any:
    """Embeddings mock so the app can render without an API key."""

    class MockEmbeddings:
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.1] * 1536 for _ in texts]

        def embed_query(self, text: str) -> list[float]:
            return [0.1] * 1536

    return MockEmbeddings()


def _mock_llm() -> Any:
    """LLM mock that keeps the UI usable in demo mode."""

    class MockLLM:
        def invoke(self, messages: list[Any]) -> AIMessage:
            return AIMessage(
                content=(
                    "[Demo mode] Set OPENAI_API_KEY for live grounded answers. "
                    "The interface is ready, but generation is currently mocked."
                )
            )

    return MockLLM()


def get_engine() -> Any:
    """Create a configured RAG engine instance."""
    from src.rag_engine import RAGEngine
    from src.vector_store import PolicyVectorStore

    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "chroma_data")
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if api_key:
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            tiktoken_enabled=False,
            check_embedding_ctx_length=False,
        )
        llm = ChatOpenAI(
            model=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            temperature=0,
        )
    else:
        embeddings = _mock_embeddings()
        llm = _mock_llm()

    store = PolicyVectorStore(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name="vectix_policies",
    )
    return RAGEngine(vector_store=store, llm=llm)
