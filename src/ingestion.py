"""
Document ingestion for the VectixLogic policy RAG corpus.

Supports Markdown, TXT, HTML, and PDF files. Parsing is deterministic:
files are loaded in sorted path order and chunking settings are fixed.
"""

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, List

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownTextSplitter

# Match "**Policy ID:** VL-SEC-013" or "Policy ID: VL-SEC-013"
POLICY_ID_PATTERN = re.compile(
    r"\*\*Policy\s+ID:\*\*\s*([A-Z0-9\-]+)|Policy\s+ID:\s*([A-Z0-9\-]+)",
    re.IGNORECASE,
)

SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".html", ".htm", ".pdf"}
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


class _HTMLTextExtractor(HTMLParser):
    """Minimal HTML-to-text parser for policy ingestion."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self._parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self._parts)


class DocumentLoader:
    """Load policy documents from disk and split them into chunks."""

    def __init__(
        self,
        directory_path: str,
        glob: str = "**/*",
    ) -> None:
        self._directory_path = Path(directory_path).resolve()
        self._glob = glob
        self._splitter = MarkdownTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    def load(self) -> List[Document]:
        """Load all supported documents from the directory."""
        return [self._load_path(path) for path in self._iter_supported_files()]

    def load_and_chunk(self) -> List[Document]:
        """Load documents, attach citation metadata, and split into chunks."""
        documents = self.load()
        for doc in documents:
            match = POLICY_ID_PATTERN.search(doc.page_content)
            if match:
                policy_id = (match.group(1) or match.group(2) or "").strip()
                if policy_id:
                    doc.metadata["policy_id"] = policy_id
        return self._splitter.split_documents(documents)

    def _iter_supported_files(self) -> Iterable[Path]:
        """Yield supported files in deterministic path order."""
        for path in sorted(self._directory_path.glob(self._glob)):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield path

    def _load_path(self, path: Path) -> Document:
        """Convert one source file into a LangChain Document."""
        suffix = path.suffix.lower()
        content = self._read_file(path, suffix)
        return Document(
            page_content=content,
            metadata={
                "source": str(path),
                "title": path.stem.replace("_", " ").replace("-", " ").title(),
                "file_type": suffix.lstrip("."),
            },
        )

    def _read_file(self, path: Path, suffix: str) -> str:
        """Read content from one file based on extension."""
        if suffix in {".md", ".markdown", ".txt"}:
            return path.read_text(encoding="utf-8")
        if suffix in {".html", ".htm"}:
            parser = _HTMLTextExtractor()
            parser.feed(path.read_text(encoding="utf-8"))
            return parser.get_text()
        if suffix == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError("PDF ingestion requires pypdf to be installed.") from exc
            reader = PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        raise ValueError(f"Unsupported file type for ingestion: {suffix}")
