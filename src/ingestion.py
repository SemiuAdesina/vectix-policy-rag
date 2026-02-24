"""
Document ingestion for the VectixLogic policy RAG corpus.

Loads Markdown files from a directory using LangChain's DirectoryLoader
and optionally chunks them with MarkdownTextSplitter for vector storage.
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownTextSplitter


# Configurable chunking for reproducible evaluation (per .cursorrules)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


class DocumentLoader:
    """
    Loads Markdown policy documents from a directory.

    Uses LangChain DirectoryLoader with a Markdown-friendly text loader
    so that all .md files are discovered and loaded. Supports optional
    chunking via MarkdownTextSplitter for RAG indexing.
    """

    def __init__(
        self,
        directory_path: str,
        glob: str = "**/*.md",
    ) -> None:
        """
        Initialize the loader with a directory path.

        Args:
            directory_path: Path to the directory containing .md files.
            glob: Glob pattern for file discovery. Defaults to all .md files.
        """
        self._directory_path = Path(directory_path).resolve()
        self._glob = glob
        self._loader = DirectoryLoader(
            str(self._directory_path),
            glob=glob,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        self._splitter = MarkdownTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    def load(self) -> List[Document]:
        """
        Load all Markdown documents from the directory (one Document per file).

        Returns:
            List of LangChain Document objects, one per .md file.
        """
        return self._loader.load()

    def load_and_chunk(self) -> List[Document]:
        """
        Load documents and split into chunks using MarkdownTextSplitter.

        Use this for building the vector store so that retrieval operates
        on semantic chunks rather than whole files.

        Returns:
            List of chunked Document objects.
        """
        documents = self.load()
        return self._splitter.split_documents(documents)
