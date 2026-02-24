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

    def test_loader_ignores_non_markdown_files(self) -> None:
        """Loader returns only .md files; .txt and other extensions are ignored."""
        # Arrange: directory with 3 .md and 2 .txt
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            for i in range(3):
                (base / f"doc_{i}.md").write_text("# Markdown\n\nBody.", encoding="utf-8")
            (base / "notes.txt").write_text("Not markdown", encoding="utf-8")
            (base / "readme.txt").write_text("Also not", encoding="utf-8")

            loader = DocumentLoader(directory_path=str(base))

            # Act
            documents = loader.load()

            # Assert: only 3 documents (the .md files)
            self.assertEqual(len(documents), 3, "Only .md files should be loaded")
