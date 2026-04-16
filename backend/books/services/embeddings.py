from __future__ import annotations

import hashlib
import math
from typing import Dict, List

from django.conf import settings

try:
    import chromadb
except Exception:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


class EmbeddingService:
    def __init__(self) -> None:
        self.model = None
        self.client = None
        self.collection = None
        self._query_cache: Dict[str, List[float]] = {}
        self._book_hash_cache: Dict[int, str] = {}
        self._memory_store: Dict[str, Dict] = {}

    def _ensure_backends(self) -> None:
        if self.model is None and SentenceTransformer is not None:
            try:
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            except Exception:
                self.model = None

        if self.collection is None and chromadb is not None:
            try:
                self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
                self.collection = self.client.get_or_create_collection(name="books")
            except Exception:
                self.client = None
                self.collection = None

    def chunk_text(self, text: str, chunk_size: int | None = None, overlap: int | None = None) -> List[str]:
        if not text:
            return []

        chunk_size = chunk_size or settings.BOOK_CHUNK_SIZE
        overlap = overlap or settings.BOOK_CHUNK_OVERLAP
        chunk_size = max(100, chunk_size)
        overlap = max(0, min(overlap, chunk_size // 2))

        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start = end - overlap
        return chunks

    def upsert_book(self, book) -> int:
        self._ensure_backends()
        text_hash = hashlib.sha256(book.description.encode("utf-8")).hexdigest()
        if self._book_hash_cache.get(book.id) == text_hash:
            return 0

        chunks = self.chunk_text(book.description)
        if not chunks:
            return 0

        embeddings = [self._embed_text(chunk) for chunk in chunks]
        ids = [f"book-{book.id}-chunk-{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "book_id": book.id,
                "title": book.title,
                "author": book.author,
                "book_url": book.book_url,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        if self.collection is not None:
            self.collection.upsert(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        else:
            for item_id, document, vector, metadata in zip(ids, chunks, embeddings, metadatas):
                self._memory_store[item_id] = {
                    "id": item_id,
                    "document": document,
                    "embedding": vector,
                    "metadata": metadata,
                }
        self._book_hash_cache[book.id] = text_hash
        return len(chunks)

    def embed_query(self, query: str) -> List[float]:
        self._ensure_backends()
        cache_key = hashlib.sha256(query.encode("utf-8")).hexdigest()
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]
        embedding = self._embed_text(query)
        self._query_cache[cache_key] = embedding
        return embedding

    def similarity_search(self, query: str, top_k: int = 5) -> dict:
        if top_k < 1:
            top_k = 1
        query_embedding = self.embed_query(query)
        if self.collection is not None:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

        ranked = []
        for item in self._memory_store.values():
            distance = self._cosine_distance(query_embedding, item["embedding"])
            ranked.append((distance, item))

        ranked.sort(key=lambda x: x[0])
        top = ranked[:top_k]
        return {
            "documents": [[entry[1]["document"] for entry in top]],
            "metadatas": [[entry[1]["metadata"] for entry in top]],
            "distances": [[entry[0] for entry in top]],
        }

    def _embed_text(self, text: str) -> List[float]:
        if self.model is not None:
            return self.model.encode([text], convert_to_tensor=False)[0].tolist()

        tokens = [tok for tok in text.lower().split() if tok]
        size = 128
        vector = [0.0] * size
        if not tokens:
            return vector
        for token in tokens:
            idx = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % size
            vector[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    @staticmethod
    def _cosine_distance(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        similarity = dot / (na * nb)
        return 1.0 - similarity


embedding_service = EmbeddingService()
