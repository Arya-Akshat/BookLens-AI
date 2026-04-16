from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book
from .serializers import AskSerializer, BookSerializer
from .services.ai_insights import ai_insights_service
from .services.embeddings import embedding_service
from .services.rag_pipeline import rag_pipeline
from .services.scraper import SeleniumBookScraper


class BookListAPIView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class BookDetailAPIView(APIView):
    def get(self, request, pk: int):
        book = get_object_or_404(Book, pk=pk)
        serialized = BookSerializer(book).data
        serialized["ai_insights"] = {
            "summary": ai_insights_service.summarize(book.title, book.description),
            "genre": ai_insights_service.classify_genre(book.description),
        }
        return Response(serialized)


class BookUploadAPIView(APIView):
    def post(self, request):
        book_url = request.data.get("book_url")
        pages = int(request.data.get("pages", 1))
        bulk = bool(request.data.get("bulk", True))

        scraper = SeleniumBookScraper(headless=True)
        if book_url and not bulk:
            scraped_data = [scraper.scrape_single_book(book_url)]
        else:
            scraped_data = scraper.scrape_books(pages=pages)

        scraped_data = [item for item in scraped_data if item]
        created_or_updated = []

        def save_item(item):
            book, created = Book.objects.update_or_create(
                book_url=item["book_url"],
                defaults={
                    "title": item["title"],
                    "author": item["author"],
                    "description": item["description"],
                    "rating": item["rating"],
                    "reviews_count": item["reviews_count"],
                },
            )
            embedding_service.upsert_book(book)
            return book.id, created

        use_threading = connection.vendor != "sqlite" and len(scraped_data) > 1
        if use_threading:
            with ThreadPoolExecutor(max_workers=4) as executor:
                for result in executor.map(save_item, scraped_data):
                    created_or_updated.append(result)
        else:
            for item in scraped_data:
                created_or_updated.append(save_item(item))

        return Response(
            {
                "message": "Books processed successfully",
                "total": len(created_or_updated),
                "book_ids": [book_id for book_id, _ in created_or_updated],
            },
            status=status.HTTP_201_CREATED,
        )


class BookRecommendAPIView(APIView):
    def get(self, request, pk: int):
        book = get_object_or_404(Book, pk=pk)
        candidates = Book.objects.exclude(pk=pk)
        recommendations = ai_insights_service.recommend_books(book, candidates, limit=5)
        return Response({"book_id": pk, "recommendations": recommendations})


class AskAPIView(APIView):
    def post(self, request):
        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]
        top_k = serializer.validated_data.get("top_k")

        result = rag_pipeline.ask(question=question, top_k=top_k)
        return Response(result)
