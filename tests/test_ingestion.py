"""
Tests for the ingestion module.

Follows AAA (Arrange-Act-Assert) and TDD. Verifies that the Loader
discovers and loads all Markdown files from a directory.
"""

import tempfile
from pathlib import Path
from unittest import TestCase

from src.ingestion import DocumentLoader


class TestDocumentLoaderFindsAllMarkdownFiles(TestCase):
    """Verify DocumentLoader discovers and loads all .md files in a directory."""

    def test_loader_returns_twenty_documents_from_twenty_markdown_files(self) -> None:
        """Loader returns exactly 20 Document instances when directory has 20 .md files."""
        # Arrange: temporary directory with exactly 20 .md files
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            for i in range(20):
                (base / f"policy_{i:02d}.md").write_text(
                    f"# Policy {i}\n\nContent for policy {i}.",
                    encoding="utf-8",
                )

            loader = DocumentLoader(directory_path=str(base))

            # Act: load documents from the directory
            documents = loader.load()

            # Assert: 20 documents returned, each with non-empty page_content
            self.assertEqual(len(documents), 20, "Loader should return 20 documents")
            for i, doc in enumerate(documents):
                self.assertIn("page_content", dir(doc), "Each item should be a Document-like object")
                self.assertIsInstance(doc.page_content, str, "page_content should be a string")
                self.assertGreater(
                    len(doc.page_content.strip()), 0,
                    f"Document {i} should have non-empty content",
                )

    def test_loader_supports_markdown_text_and_html_files(self) -> None:
        """Loader returns supported formats and ignores unsupported ones."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            for i in range(3):
                (base / f"doc_{i}.md").write_text("# Markdown\n\nBody.", encoding="utf-8")
            (base / "notes.txt").write_text("Plain text policy", encoding="utf-8")
            (base / "policy.html").write_text("<html><body><h1>HTML Policy</h1><p>Remote work body.</p></body></html>", encoding="utf-8")
            (base / "ignore.json").write_text('{"skip": true}', encoding="utf-8")

            loader = DocumentLoader(directory_path=str(base))

            documents = loader.load()

            self.assertEqual(len(documents), 5, "Supported file types should be loaded")
            contents = [doc.page_content for doc in documents]
            self.assertTrue(any("Plain text policy" in content for content in contents))
            self.assertTrue(any("HTML Policy" in content for content in contents))

    def test_load_and_chunk_extracts_policy_id_into_chunk_metadata(self) -> None:
        """Chunk metadata preserves the policy identifier for citations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "policy.md").write_text(
                "# Remote Work Policy\n\n**Policy ID:** VL-HR-001\n\nEmployees must be online during core hours.",
                encoding="utf-8",
            )

            loader = DocumentLoader(directory_path=str(base))

            chunks = loader.load_and_chunk()

            self.assertGreaterEqual(len(chunks), 1, "Chunking should return at least one chunk")
            self.assertEqual(chunks[0].metadata.get("policy_id"), "VL-HR-001")
