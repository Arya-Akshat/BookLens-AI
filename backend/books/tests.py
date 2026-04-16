from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book


class BookAPITests(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            description="A fantasy adventure with a reluctant hero and a dangerous quest.",
            rating=4.7,
            reviews_count=1520,
            book_url="https://example.com/hobbit",
        )

    @patch("books.views.embedding_service.upsert_book")
    @patch("books.views.SeleniumBookScraper.scrape_books")
    def test_book_upload_api(self, mock_scrape_books, mock_upsert):
        mock_scrape_books.return_value = [
            {
                "title": "Dune",
                "author": "Frank Herbert",
                "description": "Space politics and prophecy on a desert planet.",
                "rating": 4.5,
                "reviews_count": 900,
                "book_url": "https://example.com/dune",
            }
        ]
        mock_upsert.return_value = 1

        response = self.client.post(reverse("book-upload"), {"pages": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total"], 1)
        self.assertTrue(Book.objects.filter(book_url="https://example.com/dune").exists())

    @patch("books.views.rag_pipeline.ask")
    def test_ask_endpoint(self, mock_ask):
        mock_ask.return_value = {
            "question": "What is this about?",
            "answer": "It is a fantasy quest story [1].",
            "sources": [
                {
                    "book_id": self.book.id,
                    "title": self.book.title,
                    "author": self.book.author,
                    "book_url": self.book.book_url,
                }
            ],
            "citations": ["[1]"],
        }

        response = self.client.post(reverse("ask"), {"question": "What is this about?"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("answer", response.data)
        self.assertEqual(len(response.data["sources"]), 1)

    def test_recommendation_api(self):
        Book.objects.create(
            title="The Name of the Wind",
            author="Patrick Rothfuss",
            description="Magic, university intrigue, and a legendary hero.",
            rating=4.6,
            reviews_count=1300,
            book_url="https://example.com/name-of-the-wind",
        )
        Book.objects.create(
            title="Gone Girl",
            author="Gillian Flynn",
            description="A dark mystery around a missing wife.",
            rating=4.1,
            reviews_count=2100,
            book_url="https://example.com/gone-girl",
        )

        url = reverse("book-recommend", kwargs={"pk": self.book.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recommendations", response.data)
        self.assertGreaterEqual(len(response.data["recommendations"]), 1)
