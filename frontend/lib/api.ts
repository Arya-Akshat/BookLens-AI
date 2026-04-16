export type Book = {
  id: number;
  title: string;
  author: string;
  description: string;
  rating: number;
  reviews_count: number;
  book_url: string;
  created_at: string;
  ai_insights?: {
    summary: string;
    genre: string;
  };
};

export type AskResponse = {
  question: string;
  answer: string;
  sources: {
    book_id: number;
    title: string;
    author: string;
    book_url: string;
  }[];
  citations: string[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }

  return response.json() as Promise<T>;
}

export const api = {
  getBooks: () => apiFetch<Book[]>("/books/"),
  getBook: (id: string | number) => apiFetch<Book>(`/books/${id}/`),
  getRecommendations: (id: string | number) =>
    apiFetch<{ book_id: number; recommendations: Book[] }>(`/books/recommend/${id}/`),
  askQuestion: (question: string, top_k = 5) =>
    apiFetch<AskResponse>("/ask/", {
      method: "POST",
      body: JSON.stringify({ question, top_k })
    }),
  uploadBooks: (payload: { pages?: number; book_url?: string; bulk?: boolean }) =>
    apiFetch<{ message: string; total: number; book_ids: number[] }>("/books/upload/", {
      method: "POST",
      body: JSON.stringify(payload)
    })
};
