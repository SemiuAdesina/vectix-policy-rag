"""Helper utilities for ranking and presenting retrieved policy chunks."""

import re
from typing import List, Optional

from langchain_core.documents import Document

TOKEN_PATTERN = re.compile(r"[a-z0-9\-]{2,}")
POLICY_ID_REF_PATTERN = re.compile(r"\bVL-[A-Z]+-\d+(?:-[A-Z]+)?\b", re.IGNORECASE)
UNSUPPORTED_PATTERNS = [
    "context does not contain",
    "cannot provide an answer based on the available policies",
    "no policy context for that question",
    "i can only answer",
    "do not contain relevant information",
]


def rerank_docs(query: str, docs: List[Document], k: int) -> List[Document]:
    """Rerank retrieved docs with lightweight lexical overlap before generation."""
    query_tokens = set(TOKEN_PATTERN.findall(query.lower()))
    if not query_tokens:
        return docs[:k]

    scored = [(_score_doc(query_tokens, doc), -index, doc) for index, doc in enumerate(docs)]
    scored.sort(reverse=True)
    positive = [doc for score, _, doc in scored if score > 0]
    reranked = positive or [doc for _, _, doc in scored]
    return reranked[:k]


def extract_sources(docs: List[Document], preferred: Optional[List[str]] = None) -> List[str]:
    """Extract unique source identifiers; prefer policy IDs over file paths."""
    seen = set()
    out = []
    for doc in docs:
        source = doc_source(doc)
        if source and source not in seen:
            seen.add(source)
            out.append(str(source))
    if not preferred:
        return out
    preferred_upper = [source.upper() for source in preferred]
    prioritized = [source for source in preferred_upper if source in out]
    remainder = [source for source in out if source not in prioritized]
    return prioritized + remainder


def extract_cited_policy_ids(answer: str) -> List[str]:
    """Return cited policy ids mentioned directly in the model answer."""
    seen = set()
    cited = []
    for match in POLICY_ID_REF_PATTERN.findall(answer or ""):
        normalized = match.upper()
        if normalized not in seen:
            seen.add(normalized)
            cited.append(normalized)
    return cited


def answer_is_unsupported(answer: str) -> bool:
    """Return True when the model is explicitly refusing or lacks support."""
    normalized = (answer or "").strip().lower()
    return any(pattern in normalized for pattern in UNSUPPORTED_PATTERNS)


def build_display_chunks(
    docs: List[Document],
    cited_sources: Optional[List[str]] = None,
    limit: int = 3,
) -> List[dict]:
    """Return compact evidence cards for the UI, preferring cited sources."""
    preferred_sources = set(source.upper() for source in (cited_sources or []))
    seen_sources = set()
    chunks = []
    for doc in _prioritize_docs_by_source(docs, preferred_sources):
        source = doc_source(doc)
        if source in seen_sources:
            continue
        seen_sources.add(source)
        chunks.append({"content": clean_display_text(doc.page_content), "source": source})
        if len(chunks) >= limit:
            break
    if chunks:
        return chunks
    return [{"content": clean_display_text(doc.page_content), "source": doc_source(doc)} for doc in docs[:limit]]


def doc_source(doc: Document) -> str:
    """Return the preferred source label for one retrieved document."""
    meta = doc.metadata or {}
    return str(meta.get("policy_id") or meta.get("id") or meta.get("source") or "—")


def clean_display_text(text: str) -> str:
    """Convert raw markdown-heavy chunk text into a cleaner evidence excerpt."""
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line == "---" or re.fullmatch(r"\|?[\-\s:|]+\|?", line):
            continue
        if line.startswith("|"):
            line = " ".join(part.strip() for part in line.strip("|").split("|") if part.strip())
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = line.replace("**", "").replace("`", "")
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)
    excerpt = " ".join(lines[:4])
    return excerpt[:420] + ("..." if len(excerpt) > 420 else "")


def _score_doc(query_tokens: set[str], doc: Document) -> int:
    """Score a document by lexical overlap with the query."""
    text = doc.page_content.lower()
    doc_tokens = set(TOKEN_PATTERN.findall(text))
    overlap = len(query_tokens & doc_tokens)
    phrase_bonus = sum(1 for token in query_tokens if token in text)
    source_bonus = sum(2 for token in query_tokens if token in doc_source(doc).lower())
    return overlap * 3 + phrase_bonus + source_bonus


def _prioritize_docs_by_source(docs: List[Document], preferred_sources: set[str]) -> List[Document]:
    """Move cited-source docs to the front while preserving relative order."""
    if not preferred_sources:
        return docs
    cited_docs = [doc for doc in docs if doc_source(doc).upper() in preferred_sources]
    other_docs = [doc for doc in docs if doc_source(doc).upper() not in preferred_sources]
    return cited_docs + other_docs
