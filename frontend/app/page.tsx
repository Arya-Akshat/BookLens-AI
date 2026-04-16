import Link from "next/link";
import BookCard from "@/components/BookCard";
import { api, Book } from "@/lib/api";

export default async function DashboardPage() {
  let books: Book[] = [];
  try {
    books = await api.getBooks();
  } catch {
    books = [];
  }

  return (
    <section className="space-y-8">
      <header className="space-y-4">
        <p className="text-sm uppercase tracking-[0.2em] text-ink/70">Document Intelligence Platform</p>
        <h1 className="font-[var(--font-serif)] text-4xl font-semibold leading-tight text-ink md:text-5xl">
          Explore books with scraping, embeddings, and grounded AI answers.
        </h1>
        <div className="flex flex-wrap gap-3">
          <Link href="/ask" className="rounded-xl bg-flame px-4 py-2 font-semibold text-white hover:brightness-110">
            Open Q&A
          </Link>
          <a
            href="http://127.0.0.1:8000/api/books/"
            target="_blank"
            rel="noreferrer"
            className="rounded-xl border border-ink/20 px-4 py-2 font-semibold text-ink"
          >
            API Endpoint
          </a>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-2">
        {books.length === 0 ? (
          <div className="card p-6">
            <p className="text-sm text-ink/80">
              No books available yet. Run sample loader or use the upload API to scrape books.
            </p>
          </div>
        ) : (
          books.map((book) => <BookCard key={book.id} book={book} />)
        )}
      </section>
    </section>
  );
}
