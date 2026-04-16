import Link from "next/link";
import { api } from "@/lib/api";

type BookDetailProps = {
  params: {
    id: string;
  };
};

export default async function BookDetailPage({ params }: BookDetailProps) {
  const book = await api.getBook(params.id);
  const recommendationPayload = await api.getRecommendations(params.id);

  return (
    <section className="space-y-6">
      <Link href="/" className="text-sm text-tide underline underline-offset-4">
        Back to Dashboard
      </Link>
      <article className="card space-y-4 p-6">
        <h1 className="font-[var(--font-serif)] text-3xl font-semibold text-ink">{book.title}</h1>
        <p className="text-ink/70">By {book.author}</p>
        <div className="flex gap-4 text-sm text-ink/80">
          <span>Rating: {book.rating.toFixed(1)}</span>
          <span>Reviews: {book.reviews_count}</span>
        </div>
        <p className="leading-7 text-ink/90">{book.description}</p>
        <a href={book.book_url} target="_blank" rel="noreferrer" className="text-tide underline underline-offset-4">
          View Original Source
        </a>
      </article>

      <article className="card p-6">
        <h2 className="mb-3 text-xl font-semibold text-ink">AI Insights</h2>
        <p className="text-sm text-ink/80">Genre: {book.ai_insights?.genre || "general"}</p>
        <div className="mt-4 whitespace-pre-wrap rounded-lg bg-white p-4 text-sm leading-6 text-ink/90">
          {book.ai_insights?.summary || "No summary generated."}
        </div>
      </article>

      <article className="card p-6">
        <h2 className="mb-3 text-xl font-semibold text-ink">Recommendations</h2>
        <ul className="space-y-3 text-sm">
          {recommendationPayload.recommendations.map((item) => (
            <li key={item.id} className="rounded-lg bg-white p-4">
              <p className="font-semibold text-ink">{item.title}</p>
              <p className="text-ink/70">{item.author}</p>
              <p className="text-ink/70">Rating: {item.rating.toFixed(1)}</p>
            </li>
          ))}
        </ul>
      </article>
    </section>
  );
}
