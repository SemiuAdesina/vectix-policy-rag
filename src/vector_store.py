"""
Vector storage for the VectixLogic policy RAG corpus.

Handles local persistence of embedded policy chunks using ChromaDB via
LangChain. Uses dependency injection for the embedding function (Embeddings).
"""

from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class PolicyVectorStore:
    """
    Handles local persistence of embedded policy chunks using ChromaDB.

    Accepts an Embeddings instance via dependency injection (strategy pattern
    for OpenAI vs HuggingFace). Per .cursorrules: pass the Vector Store into
    the RAG chain rather than hardcoding the connection.
    """

    def __init__(
        self,
        persist_directory: str,
        embedding_function: Embeddings,
        collection_name: str = "vectix_policies",
    ) -> None:
        """
        Initialize the vector store.

        Args:
            persist_directory: Path for ChromaDB persistence.
            embedding_function: LangChain Embeddings (embed_documents, embed_query).
            collection_name: Chroma collection name.
        """
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function
        self.collection_name = collection_name
        self._vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory=persist_directory,
        )

    def add_documents(self, documents: List[Document]) -> None:
        """
        Embeds and adds Document objects to the store.

        Metadata is sanitized for ChromaDB (str, int, float, bool only).

        Args:
            documents: LangChain Document objects (page_content + metadata).
        """
        sanitized = [
            Document(
                page_content=d.page_content,
                metadata={
                    k: v
                    for k, v in d.metadata.items()
                    if isinstance(v, (str, int, float, bool))
                },
            )
            for d in documents
        ]
        self._vector_store.add_documents(sanitized)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Returns the top-k most relevant Document chunks.

        Args:
            query: Search query text.
            k: Number of results to return.

        Returns:
            List of Document objects (page_content and metadata).
        """
        return self._vector_store.similarity_search(query, k=k)
