"use client";

import { useState } from "react";
import { api, AskResponse, Book } from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";

type SourceInsight = {
  book: Book;
  recommendations: Array<{
    id: number;
    title: string;
    author: string;
    rating: number;
    book_url: string;
  }>;
};

export default function AskForm() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [sourceInsight, setSourceInsight] = useState<SourceInsight | null>(null);
  const [insightLoading, setInsightLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setSourceInsight(null);

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    try {
      setLoading(true);
      const response = await api.askQuestion(question);
      setResult(response);

      const primarySource = response.sources[0];
      if (primarySource?.book_id) {
        setInsightLoading(true);
        try {
          const [book, recPayload] = await Promise.all([
            api.getBook(primarySource.book_id),
            api.getRecommendations(primarySource.book_id)
          ]);
          setSourceInsight({ book, recommendations: recPayload.recommendations });
        } catch {
          setSourceInsight(null);
        } finally {
          setInsightLoading(false);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to query API.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card p-6">
      <form onSubmit={onSubmit} className="space-y-4">
        <label className="block text-sm font-semibold text-ink">Ask a question about the books</label>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          rows={4}
          className="w-full rounded-xl border border-ink/20 bg-white px-4 py-3 text-sm outline-none ring-flame/30 transition focus:ring"
          placeholder="Example: Which fantasy books focus on unlikely heroes?"
        />
        <button
          type="submit"
          className="rounded-xl bg-tide px-4 py-2 font-semibold text-white transition hover:brightness-110"
          disabled={loading}
        >
          Ask
        </button>
      </form>

      <div className="mt-6">
        {loading && <LoadingSpinner label="Generating answer with RAG..." />}
        {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        {result && (
          <div className="space-y-4 text-sm">
            <div>
              <h3 className="font-semibold text-ink">Answer</h3>
              <p className="mt-2 whitespace-pre-wrap rounded-lg bg-white p-4 text-ink/90">{result.answer}</p>
            </div>
            <div>
              <h4 className="font-semibold text-ink">Sources</h4>
              <ul className="mt-2 space-y-2">
                {result.sources.map((source) => (
                  <li key={`${source.book_id}-${source.book_url}`} className="rounded-lg bg-white p-3">
                    <p className="font-medium">{source.title}</p>
                    <p className="text-ink/70">{source.author}</p>
                    <a
                      href={source.book_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-tide underline underline-offset-4"
                    >
                      {source.book_url}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-ink">Book Insights</h4>
              {insightLoading && <LoadingSpinner label="Loading summary, genre, and recommendations..." />}
              {!insightLoading && sourceInsight && (
                <div className="mt-2 space-y-3">
                  <div className="rounded-lg bg-white p-3">
                    <p className="font-semibold text-ink">{sourceInsight.book.title}</p>
                    <p className="text-ink/70">Genre: {sourceInsight.book.ai_insights?.genre || "general"}</p>
                    <p className="mt-2 whitespace-pre-wrap text-ink/90">
                      {sourceInsight.book.ai_insights?.summary || "No summary available."}
                    </p>
                  </div>

                  <div className="rounded-lg bg-white p-3">
                    <p className="font-semibold text-ink">Recommendations</p>
                    {sourceInsight.recommendations.length === 0 ? (
                      <p className="text-ink/70">No recommendations found.</p>
                    ) : (
                      <ul className="mt-2 space-y-2">
                        {sourceInsight.recommendations.map((item) => (
                          <li key={item.id} className="rounded-md border border-ink/10 p-2">
                            <p className="font-medium text-ink">{item.title}</p>
                            <p className="text-ink/70">{item.author}</p>
                            <p className="text-ink/70">Rating: {item.rating.toFixed(1)}</p>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
