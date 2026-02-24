"""
Tests for the RAG engine module.

Follows TDD and AAA. Mocks LLM and vector store to avoid API calls and
verify retrieval + generation alignment (e.g. eq-006 Solana RPC scenario).
"""

from unittest import TestCase
from unittest.mock import MagicMock

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from src.rag_engine import RAGEngine


class TestRAGEngine(TestCase):
    """Verify RAG retrieval and generation with guardrails and citations."""

    def test_solana_rpc_scenario_returns_grounded_answer_with_citation(self) -> None:
        """eq-006: Answer contains expected terms and cites VL-SEC-019."""
        # Arrange: mock vector store returns Solana RPC chunk; mock LLM returns fixed answer
        mock_store = MagicMock()
        mock_store.similarity_search.return_value = [
            Document(
                page_content="Solana RPC endpoint unreachable: switch to backup RPC (Helius, QuickNode). Owner: Blockchain Lead.",
                metadata={"source": "business_continuity_v2.md", "id": "VL-SEC-019"},
            ),
        ]
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="Per VL-SEC-019, switch to a backup RPC provider (e.g. Helius or QuickNode), update env var and redeploy. Owner: Blockchain Lead."
        )
        engine = RAGEngine(vector_store=mock_store, llm=mock_llm)

        # Act
        result = engine.ask("What if the Solana RPC endpoint is unreachable?", k=1)

        # Assert
        self.assertIn("answer", result)
        self.assertIn("sources", result)
        answer = result["answer"].lower()
        self.assertTrue(
            any(term in answer for term in ["blockchain lead", "helius", "quicknode", "vl-sec-019"]),
            "Answer should contain expected terms or Policy ID",
        )
        self.assertGreater(len(result["sources"]), 0, "Should cite at least one source")

    def test_refuses_when_no_relevant_context(self) -> None:
        """When retrieval returns empty, response indicates out-of-corpus or no context."""
        # Arrange: empty retrieval
        mock_store = MagicMock()
        mock_store.similarity_search.return_value = []
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="I have no policy context for that question. Please ask about VectixLogic policies."
        )
        engine = RAGEngine(vector_store=mock_store, llm=mock_llm)

        # Act
        result = engine.ask("What is the meaning of life?", k=2)

        # Assert
        self.assertIn("answer", result)
        self.assertEqual(len(result["sources"]), 0)

    def test_latency_tracking_records_request(self) -> None:
        """Latency decorator records each request; get_latency_percentiles returns p50/p95."""
        from src.rag_engine import get_latency_percentiles, _latency_ms

        # Arrange: clear and run one request
        _latency_ms.clear()
        mock_store = MagicMock()
        mock_store.similarity_search.return_value = [
            Document(page_content="Test.", metadata={"id": "VL-TEST"}),
        ]
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Test answer.")
        engine = RAGEngine(vector_store=mock_store, llm=mock_llm)

        # Act
        engine.ask("Test?", k=1)
        percentiles = get_latency_percentiles()

        # Assert
        self.assertEqual(len(_latency_ms), 1)
        self.assertIsNotNone(percentiles["p50_ms"])
        self.assertIsNotNone(percentiles["p95_ms"])
