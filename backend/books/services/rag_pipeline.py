from __future__ import annotations

from typing import Dict, List

import requests
from django.conf import settings
from django.core.cache import cache

from .embeddings import embedding_service


class RAGPipeline:
    def ask(self, question: str, top_k: int | None = None) -> Dict:
        top_k = top_k or settings.RAG_TOP_K
        cache_key = f"rag:{question}:{top_k}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        search_results = embedding_service.similarity_search(question, top_k=top_k)
        documents = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]

        context_lines = []
        sources = []
        seen_ids = set()

        for idx, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
            context_lines.append(f"[{idx}] {doc}")
            book_id = meta.get("book_id")
            if book_id not in seen_ids:
                sources.append(
                    {
                        "book_id": book_id,
                        "title": meta.get("title", "Unknown"),
                        "author": meta.get("author", "Unknown"),
                        "book_url": meta.get("book_url", ""),
                    }
                )
                seen_ids.add(book_id)

        context = "\n\n".join(context_lines)
        prompt = (
            "Answer the user question based only on the provided context. "
            "Use concise language and mention citation markers like [1], [2].\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        )

        answer = self._call_llm(prompt)
        if not answer:
            answer = "I could not generate a model response. Here are the relevant excerpts with citations.\n" + context

        result = {
            "question": question,
            "answer": answer,
            "sources": sources,
            "citations": [f"[{i}]" for i in range(1, len(context_lines) + 1)],
        }
        cache.set(cache_key, result, timeout=600)
        return result

    def _call_llm(self, prompt: str) -> str | None:
        try:
            if settings.GROQ_API_KEY:
                from openai import OpenAI

                client = OpenAI(
                    api_key=settings.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1",
                )
                completion = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a retrieval-grounded book assistant.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                )
                return completion.choices[0].message.content

            if settings.OPENAI_API_KEY:
                from openai import OpenAI

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                completion = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a retrieval-grounded book assistant.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                )
                return completion.choices[0].message.content

            response = requests.post(
                f"{settings.LM_STUDIO_BASE_URL}/chat/completions",
                json={
                    "model": settings.LM_STUDIO_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a retrieval-grounded book assistant.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                },
                timeout=40,
            )
            response.raise_for_status()
            payload = response.json()
            return payload["choices"][0]["message"]["content"]
        except Exception:
            return None


rag_pipeline = RAGPipeline()
