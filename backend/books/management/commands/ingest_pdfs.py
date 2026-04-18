from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

from django.core.management.base import BaseCommand

from books.models import Book
from books.services.embeddings import embedding_service
from pypdf import PdfReader


class Command(BaseCommand):
    help = "Ingest PDF files into the books table and rebuild vector store"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-dir",
            type=str,
            default=None,
            help="Directory to scan recursively for PDF files (defaults to project root)",
        )
        parser.add_argument(
            "--keep-existing",
            action="store_true",
            help="Keep existing book rows instead of replacing them",
        )

    def handle(self, *args, **options):
        source_dir = options.get("source_dir")
        keep_existing = bool(options.get("keep_existing"))

        base_dir = Path(__file__).resolve().parents[4]
        root_dir = Path(source_dir).expanduser().resolve() if source_dir else base_dir.parent

        if not root_dir.exists() or not root_dir.is_dir():
            self.stderr.write(self.style.ERROR(f"Invalid source directory: {root_dir}"))
            return

        pdf_paths = sorted(
            [*root_dir.rglob("*.pdf"), *root_dir.rglob("*.PDF")],
            key=lambda p: str(p).lower(),
        )
        if not pdf_paths:
            self.stderr.write(self.style.ERROR(f"No PDF files found under: {root_dir}"))
            return

        if not keep_existing:
            Book.objects.all().delete()

        ingested = 0
        skipped = 0

        for pdf_path in pdf_paths:
            text = self._extract_text(pdf_path)
            if len(text.strip()) < 50:
                skipped += 1
                continue

            title = self._title_from_filename(pdf_path.stem)
            rel_path = quote(str(pdf_path.relative_to(root_dir)).replace("\\", "/"))
            book_url = f"https://local-pdf/{rel_path}"

            Book.objects.update_or_create(
                book_url=book_url,
                defaults={
                    "title": title,
                    "author": "Unknown Author",
                    "description": text[:50000],
                    "rating": 0.0,
                    "reviews_count": 0,
                },
            )
            ingested += 1

        self._rebuild_vectors()

        self.stdout.write(
            self.style.SUCCESS(
                f"Ingested PDFs: {ingested}, Skipped PDFs: {skipped}, Total books in DB: {Book.objects.count()}"
            )
        )

    @staticmethod
    def _extract_text(pdf_path: Path) -> str:
        try:
            reader = PdfReader(str(pdf_path))
            chunks = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    chunks.append(page_text.strip())
            return "\n\n".join(chunks)
        except Exception:
            return ""

    @staticmethod
    def _title_from_filename(stem: str) -> str:
        # Remove leading hash-like prefix used by downloaded files.
        cleaned = re.sub(r"^[0-9a-fA-F]{8,}-", "", stem)
        cleaned = cleaned.replace("_", " ").replace("-", " ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned.title() if cleaned else "Untitled PDF Book"

    @staticmethod
    def _rebuild_vectors() -> None:
        embedding_service._ensure_backends()

        if embedding_service.client is not None:
            try:
                embedding_service.client.delete_collection(name="books")
            except Exception:
                pass
            embedding_service.collection = embedding_service.client.get_or_create_collection(name="books")

        embedding_service._memory_store.clear()
        embedding_service._book_hash_cache.clear()
        embedding_service._query_cache.clear()

        for book in Book.objects.all().iterator():
            embedding_service.upsert_book(book)
