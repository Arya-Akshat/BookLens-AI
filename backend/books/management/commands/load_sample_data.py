import json
from pathlib import Path

from django.core.management.base import BaseCommand

from books.models import Book
from books.services.embeddings import embedding_service


class Command(BaseCommand):
    help = "Load sample books and precompute embeddings"

    def handle(self, *args, **options):
        sample_file = Path(__file__).resolve().parents[2] / "sample_data.json"
        if not sample_file.exists():
            self.stderr.write(self.style.ERROR(f"Sample file not found: {sample_file}"))
            return

        with open(sample_file, "r", encoding="utf-8") as fp:
            payload = json.load(fp)

        total = 0
        for item in payload:
            book, _ = Book.objects.update_or_create(
                book_url=item["book_url"],
                defaults={
                    "title": item["title"],
                    "author": item["author"],
                    "description": item["description"],
                    "rating": item.get("rating", 0.0),
                    "reviews_count": item.get("reviews_count", 0),
                },
            )
            embedding_service.upsert_book(book)
            total += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {total} sample books."))
