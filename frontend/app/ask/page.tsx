import Link from "next/link";
import AskForm from "@/components/AskForm";

export default function AskPage() {
  return (
    <section className="space-y-6">
      <Link href="/" className="text-sm text-tide underline underline-offset-4">
        Back to Dashboard
      </Link>
      <header>
        <h1 className="font-[var(--font-serif)] text-4xl font-semibold text-ink">RAG Q&A</h1>
        <p className="mt-2 text-ink/80">
          Ask grounded questions over scraped and embedded book descriptions. Answers include source citations.
        </p>
      </header>
      <AskForm />
    </section>
  );
}
