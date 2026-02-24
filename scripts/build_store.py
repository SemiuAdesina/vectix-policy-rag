"""
Build Chroma vector store from data/raw/ Markdown corpus.

Run once before using Streamlit or API. Uses OpenAI embeddings if
OPENAI_API_KEY is set; otherwise a mock (for testing only).
Usage: PYTHONPATH=. python scripts/build_store.py
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from src.ingestion import DocumentLoader
from src.vector_store import PolicyVectorStore


def main() -> None:
    os.chdir(PROJECT_ROOT)
    try:
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass

    raw_dir = Path("data/raw").resolve()
    if not raw_dir.exists():
        print("Missing data/raw/. Create corpus first.")
        return
    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "chroma_data")
    persist_path = Path(persist_dir).resolve()
    persist_path.mkdir(parents=True, exist_ok=True)

    loader = DocumentLoader(directory_path=str(raw_dir))
    chunks = loader.load_and_chunk()
    print(f"Loaded {len(chunks)} chunks from {raw_dir}")

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    else:
        from src.rag_app import _mock_embeddings
        embeddings = _mock_embeddings()
        print("No OPENAI_API_KEY; using mock embeddings (demo only).")

    store = PolicyVectorStore(
        persist_directory=str(persist_path),
        embedding_function=embeddings,
        collection_name="vectix_policies",
    )
    store.add_documents(chunks)
    print(f"Vector store built at {persist_path}")


if __name__ == "__main__":
    main()
