from __future__ import annotations

import re
from typing import Dict, List

import requests
from django.conf import settings
from django.core.cache import cache


GENRE_KEYWORDS = {
    "fantasy": ["magic", "kingdom", "dragon", "sword", "myth"],
    "science fiction": ["space", "robot", "future", "alien", "planet"],
    "romance": ["love", "heart", "relationship", "kiss", "romantic"],
    "mystery": ["murder", "detective", "clue", "crime", "investigation"],
    "history": ["war", "empire", "historical", "century", "revolution"],
    "self-help": ["habit", "mindset", "growth", "productivity", "improve"],
}


class AIInsightsService:
    def classify_genre(self, description: str) -> str:
        text = self._clean_source_text(description).lower()
        scores = {
            genre: sum(keyword in text for keyword in keywords)
            for genre, keywords in GENRE_KEYWORDS.items()
        }
        best_genre, best_score = max(scores.items(), key=lambda x: x[1], default=("general", 0))
        return best_genre if best_score > 0 else "general"

    def summarize(self, title: str, description: str) -> str:
        cleaned_description = self._clean_source_text(description)
        cache_key = f"summary:{title}:{hash(description)}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        prompt = (
            "Summarize the following book in 3 concise bullet points. "
            f"Title: {title}\nDescription: {cleaned_description}"
        )
        llm_answer = self._call_llm(prompt)
        summary = llm_answer or self._fallback_summary(cleaned_description)
        cache.set(cache_key, summary, timeout=3600)
        return summary

    def recommend_books(self, book, candidate_books, limit: int = 5) -> List[Dict]:
        book_genre = self.classify_genre(book.description)
        scored = []
        for candidate in candidate_books:
            if candidate.id == book.id:
                continue
            candidate_genre = self.classify_genre(candidate.description)
            genre_score = 1.5 if candidate_genre == book_genre else 0.5
            rating_score = candidate.rating / 5.0
            review_score = min(candidate.reviews_count / 1000.0, 1.0)
            total = genre_score + rating_score + review_score
            scored.append((total, candidate))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [candidate for _, candidate in scored[:limit]]
        return [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "rating": b.rating,
                "book_url": b.book_url,
            }
            for b in top
        ]

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
                        {"role": "system", "content": "You are a concise literary analyst."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                return completion.choices[0].message.content

            if settings.OPENAI_API_KEY:
                from openai import OpenAI

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                completion = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a concise literary analyst."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                return completion.choices[0].message.content

            response = requests.post(
                f"{settings.LM_STUDIO_BASE_URL}/chat/completions",
                json={
                    "model": settings.LM_STUDIO_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a concise literary analyst."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            return payload["choices"][0]["message"]["content"]
        except Exception:
            return None

    @staticmethod
    def _fallback_summary(description: str) -> str:
        normalized = AIInsightsService._clean_source_text(description)
        sentences = [s.strip() for s in re.split(r"[.!?]", normalized) if s.strip()]
        if not sentences:
            return "No summary available."
        bullets = []
        for sentence in sentences:
            # Skip obvious source-license boilerplate in fallback summaries.
            low = sentence.lower()
            if (
                "project gutenberg" in low
                or "ebook" in low
                or "license" in low
                or "www." in low
                or "updater" in low
                or "html version" in low
                or "chapter" in low
                or "copyright" in low
            ):
                continue
            if len(sentence) < 40:
                continue
            bullets.append(sentence)
            if len(bullets) == 3:
                break
        if not bullets:
            bullets = sentences[:3]
        return "\n".join([f"- {s}." for s in bullets])

    @staticmethod
    def _clean_source_text(text: str) -> str:
        if not text:
            return ""
        # Replace tabs/newlines and squeeze repeated whitespace for cleaner prompts/UI.
        normalized = re.sub(r"\s+", " ", text).strip()
        # Remove the most common Gutenberg preamble if present.
        marker = "*** START OF THIS PROJECT GUTENBERG"
        idx = normalized.upper().find(marker)
        if idx != -1:
            normalized = normalized[idx + len(marker):].strip(" *-:;")
        # If chapter content exists, skip front matter and start from first chapter.
        ch_idx = re.search(r"\bCHAPTER\s+I\b", normalized, flags=re.I)
        if ch_idx:
            normalized = normalized[ch_idx.start():]
        # Drop bracketed notes and obvious URL clutter.
        normalized = re.sub(r"\[[^\]]{0,200}\]", " ", normalized)
        normalized = re.sub(r"https?://\S+|www\.\S+", " ", normalized)
        normalized = re.sub(r"\bCHAPTER\s+[IVXLCDM0-9]+\b", " ", normalized, flags=re.I)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized


ai_insights_service = AIInsightsService()
