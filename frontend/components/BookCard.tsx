import Link from "next/link";
import { Book } from "@/lib/api";

type BookCardProps = {
  book: Book;
};

export default function BookCard({ book }: BookCardProps) {
  return (
    <article className="card fade-in p-5">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-ink">{book.title}</h2>
          <p className="text-sm text-ink/70">{book.author}</p>
        </div>
        <span className="rounded-full bg-tide px-3 py-1 text-xs font-semibold text-white">
          {book.rating.toFixed(1)}
        </span>
      </div>
      <p className="line-clamp-3 text-sm leading-6 text-ink/90">{book.description}</p>
      <div className="mt-4 flex items-center justify-between text-sm">
        <a
          href={book.book_url}
          target="_blank"
          rel="noreferrer"
          className="text-tide underline decoration-tide/50 underline-offset-4"
        >
          Source Link
        </a>
        <Link
          href={`/books/${book.id}`}
          className="rounded-lg bg-flame px-3 py-2 font-semibold text-white transition hover:brightness-110"
        >
          View Details
        </Link>
      </div>
    </article>
  );
}
