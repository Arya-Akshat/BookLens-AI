"use client";

import { useState } from "react";
import { api, AskResponse } from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";

export default function AskForm() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setResult(null);

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    try {
      setLoading(true);
      const response = await api.askQuestion(question);
      setResult(response);
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
          </div>
        )}
      </div>
    </div>
  );
}
