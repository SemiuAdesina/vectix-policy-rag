"""
Build a Chroma vector store from the local policy corpus.

Usage:
  PYTHONPATH=. python scripts/build_store.py
"""

import os
import shutil
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
from src.reproducibility import set_reproducible_seed
from src.vector_store import PolicyVectorStore


def main() -> None:
    """Load policy documents, chunk them, and persist vectors."""
    os.chdir(PROJECT_ROOT)
    seed = set_reproducible_seed()
    raw_dir = Path("data/raw").resolve()
    if not raw_dir.exists():
        print("Missing data/raw/. Add the policy corpus before building the store.")
        return

    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "chroma_data")
    persist_path = Path(persist_dir).resolve()
    if persist_path.exists():
        shutil.rmtree(persist_path)
        print(f"Cleared existing vector store at {persist_path}")
    persist_path.mkdir(parents=True, exist_ok=True)
    print(f"Using reproducible seed {seed}")

    loader = DocumentLoader(directory_path=str(raw_dir))
    chunks = loader.load_and_chunk()
    print(f"Loaded {len(chunks)} chunks from {raw_dir}")

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if api_key:
        from langchain_openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            tiktoken_enabled=False,
            check_embedding_ctx_length=False,
        )
    else:
        from src.rag_app import _mock_embeddings

        embeddings = _mock_embeddings()
        print("No OPENAI_API_KEY found. Using demo embeddings.")

    store = PolicyVectorStore(
        persist_directory=str(persist_path),
        embedding_function=embeddings,
        collection_name="vectix_policies",
    )
    store.add_documents(chunks)
    print(f"Vector store built at {persist_path}")


if __name__ == "__main__":
    main()
