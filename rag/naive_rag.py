"""Naive RAG implementation using OpenAI Embeddings + simple cosine retriever.

Lightweight pipeline designed for Streamlit Cloud free tier:
1. Ingest documents (split into chunks, embed with OpenAI)
2. Retrieve relevant chunks via cosine similarity (no FAISS needed)
3. Generate an answer using a given LLM with the retrieved context
"""

from __future__ import annotations

import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from llms.base import BaseLLM


class NaiveRAG:
    """Simple RAG: chunk -> OpenAI embed -> cosine similarity -> retrieve -> generate."""

    def __init__(
        self,
        openai_api_key: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_model: str = "text-embedding-3-small",
        k: int = 4,
    ):
        """
        Args:
            openai_api_key: Required. OpenAI API key for embeddings.
            chunk_size: Max characters per chunk.
            chunk_overlap: Overlap between consecutive chunks.
            embedding_model: OpenAI embedding model to use.
            k: Number of chunks to retrieve.
        """
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self._embeddings = OpenAIEmbeddings(
            model=embedding_model,
            api_key=openai_api_key,
        )
        self._k = k

        # In-memory store
        self._chunks: list[str] = []
        self._sources: list[str] = []
        self._vectors: np.ndarray | None = None

    @property
    def is_ready(self) -> bool:
        return self._vectors is not None and len(self._chunks) > 0

    def ingest(self, documents: dict[str, str]) -> int:
        """Ingest a dict of {doc_id: content} into the in-memory store.

        Returns the number of chunks created.
        """
        self._chunks = []
        self._sources = []

        for doc_id, content in documents.items():
            chunks = self._splitter.split_text(content)
            for chunk in chunks:
                self._chunks.append(chunk)
                self._sources.append(doc_id)

        if not self._chunks:
            return 0

        # Embed all chunks at once
        vectors = self._embeddings.embed_documents(self._chunks)
        self._vectors = np.array(vectors, dtype=np.float32)

        return len(self._chunks)

    def _cosine_similarity(self, query_vec: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and all stored vectors."""
        # Normalize
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
        doc_norms = self._vectors / (
            np.linalg.norm(self._vectors, axis=1, keepdims=True) + 1e-10
        )
        return doc_norms @ query_norm

    def retrieve(self, query: str, k: int | None = None) -> str:
        """Retrieve the top-k most relevant chunks as a single string.

        Each chunk is prefixed with its source document ID.
        """
        if not self.is_ready:
            return ""

        k = min(k or self._k, len(self._chunks))

        # Embed query
        query_vec = np.array(
            self._embeddings.embed_query(query), dtype=np.float32
        )

        # Cosine similarity
        scores = self._cosine_similarity(query_vec)
        top_indices = np.argsort(scores)[::-1][:k]

        parts = []
        for idx in top_indices:
            source = self._sources[idx]
            parts.append(f"[{source}]: {self._chunks[idx]}")
        return "\n\n".join(parts)

    def retrieve_with_scores(self, query: str, k: int | None = None) -> list[dict]:
        """Retrieve chunks with similarity scores for debugging."""
        if not self.is_ready:
            return []

        k = min(k or self._k, len(self._chunks))
        query_vec = np.array(
            self._embeddings.embed_query(query), dtype=np.float32
        )
        scores = self._cosine_similarity(query_vec)
        top_indices = np.argsort(scores)[::-1][:k]

        return [
            {
                "content": self._chunks[idx],
                "source": self._sources[idx],
                "score": float(scores[idx]),
            }
            for idx in top_indices
        ]

    def query(self, query: str, llm: BaseLLM) -> str:
        """Full RAG pipeline: retrieve context + generate answer.

        Args:
            query: The user's question.
            llm: The LLM to use for generation.

        Returns:
            The generated answer string.
        """
        context = self.retrieve(query)
        if not context:
            return llm.simple_chat(query)

        system_prompt = (
            "Eres un asistente que responde preguntas usando SOLO la informacion "
            "proporcionada en el contexto. Cita el ID del documento entre corchetes. "
            "Si hay versiones vigentes y desactualizadas, usa siempre la VIGENTE."
        )
        user_prompt = f"CONTEXTO:\n{context}\n\nPREGUNTA: {query}"
        return llm.simple_chat(user_prompt, system_prompt=system_prompt)

    def clear(self):
        """Clear the in-memory store."""
        self._chunks = []
        self._sources = []
        self._vectors = None
