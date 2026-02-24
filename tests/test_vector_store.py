"""
Tests for the vector store module.

Follows TDD and AAA (Arrange-Act-Assert). Uses a mock embedding function
to avoid API calls and ensure deterministic tests.
"""

import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from langchain_core.documents import Document

from src.vector_store import PolicyVectorStore


class MockEmbeddings:
    """Mock embedding function that returns static vectors (no API call)."""

    def embed_documents(self, texts: list) -> list:
        """Return one vector per text; dimension 1536 for OpenAI compatibility."""
        return [[0.1] * 1536 for _ in texts]

    def embed_query(self, text: str) -> list:
        """Return a single vector for the query."""
        return [0.1] * 1536


class TestPolicyVectorStore(TestCase):
    """Verify PolicyVectorStore stores chunked docs and returns relevant results."""

    def setUp(self) -> None:
        """Arrange: temp dir and store with mock embeddings."""
        self.tmp_dir = tempfile.mkdtemp()
        self.persist_dir = str(Path(self.tmp_dir) / "chroma")
        self.embeddings = MockEmbeddings()
        self.store = PolicyVectorStore(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
            collection_name="vectix_policies",
        )

    def tearDown(self) -> None:
        """Clean up temp directory."""
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_similarity_search_returns_relevant_policy_chunks(self) -> None:
        """Solana RPC scenario chunk is returned for a domain-specific query."""
        # Arrange
        doc1 = Document(
            page_content="Core hours are 10 AM to 3 PM WAT.",
            metadata={"id": "VL-HR-001"},
        )
        doc2 = Document(
            page_content="Solana RPC endpoint down: switch to Helius or QuickNode. Owner: Blockchain Lead.",
            metadata={"id": "VL-SEC-019"},
        )
        self.store.add_documents([doc1, doc2])

        # Act
        results = self.store.similarity_search("Solana RPC endpoint down", k=2)

        # Assert
        self.assertGreaterEqual(len(results), 1)
        contents = [r.page_content for r in results]
        self.assertTrue(
            any("Solana" in c and "Blockchain Lead" in c for c in contents),
            "Results should include the Solana RPC scenario chunk",
        )

    def test_add_documents_and_search_returns_non_empty(self) -> None:
        """Adding documents and searching yields the expected chunk."""
        # Arrange
        doc = Document(
            page_content="AWS failover takes 15 minutes.",
            metadata={"id": "VL-SEC-013"},
        )
        self.store.add_documents([doc])

        # Act
        results = self.store.similarity_search("AWS failover", k=1)

        # Assert
        self.assertEqual(len(results), 1)
        self.assertIn("15 minutes", results[0].page_content)
