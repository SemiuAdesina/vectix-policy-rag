"""Tests for the FastAPI web and API endpoints."""

from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app


class _FakeEngine:
    def ask(self, query: str, k: int = 4) -> dict:
        return {
            "answer": f"Answer for: {query}",
            "sources": ["VL-HR-001"],
            "chunks": [{"source": "VL-HR-001", "content": "Core hours are 10:00 AM to 3:00 PM WAT."}],
        }


class TestPolicyApi(TestCase):
    """Verify the required web and API endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_root_serves_html_chat_interface(self) -> None:
        """Root path should serve the browser-based chat page."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("Policy Intelligence", response.text)

    def test_health_returns_ok(self) -> None:
        """Health endpoint should return a simple JSON payload."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_chat_returns_answer_sources_and_chunks(self) -> None:
        """Chat endpoint should return the structured RAG response."""
        with patch("src.rag_app.get_engine", return_value=_FakeEngine()):
            response = self.client.post("/chat", json={"query": "What are the core hours?"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("answer", payload)
        self.assertIn("sources", payload)
        self.assertIn("chunks", payload)
        self.assertEqual(payload["sources"], ["VL-HR-001"])
