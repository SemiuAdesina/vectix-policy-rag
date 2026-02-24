"""
App wiring: build RAGEngine from env (persist dir, OpenAI key).

Used by Streamlit UI and FastAPI. Uses mock LLM/embeddings if OPENAI_API_KEY not set.
Loads .env automatically if python-dotenv is installed.
"""

import os
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain_core.messages import AIMessage


def _mock_embeddings():
    """Embeddings mock for demo when OPENAI_API_KEY is not set."""
    class M:
        def embed_documents(self, texts):
            return [[0.1] * 1536 for _ in texts]
        def embed_query(self, text):
            return [0.1] * 1536
    return M()


def _mock_llm():
    """LLM mock: returns a short message so UI/API work without API key."""
    class M:
        def invoke(self, messages):
            return AIMessage(content="[Demo mode: set OPENAI_API_KEY for real answers.] Answer using the provided policy context only.")
    return M()


def get_engine() -> Any:
    """
    Build RAGEngine with vector store (from CHROMA_PERSIST_DIR) and LLM.

    Uses OpenAI embeddings + ChatOpenAI if OPENAI_API_KEY is set;
    otherwise uses mocks so the app runs for demo.
    """
    from src.rag_engine import RAGEngine
    from src.vector_store import PolicyVectorStore

    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "chroma_data")
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    else:
        embeddings = _mock_embeddings()
        llm = _mock_llm()
    store = PolicyVectorStore(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name="vectix_policies",
    )
    return RAGEngine(vector_store=store, llm=llm)
