"""
Vector storage for the VectixLogic policy RAG corpus.

Handles local persistence of embedded policy chunks using ChromaDB via
LangChain. Uses dependency injection for the embedding function.
"""

from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class PolicyVectorStore:
    """Persistent Chroma-backed vector store for policy chunks."""

    def __init__(
        self,
        persist_directory: str,
        embedding_function: Embeddings,
        collection_name: str = "vectix_policies",
    ) -> None:
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function
        self.collection_name = collection_name
        self._vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory=persist_directory,
        )

    def add_documents(self, documents: List[Document]) -> None:
        """Embed and add sanitized documents to the collection."""
        sanitized = [
            Document(
                page_content=doc.page_content,
                metadata={
                    key: value
                    for key, value in (doc.metadata or {}).items()
                    if isinstance(value, (str, int, float, bool))
                },
            )
            for doc in documents
        ]
        self._vector_store.add_documents(sanitized)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Return the top-k most relevant chunks."""
        return self._vector_store.similarity_search(query, k=k)
