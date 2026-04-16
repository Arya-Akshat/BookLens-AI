import type { Metadata } from "next";
import { Space_Grotesk, Fraunces } from "next/font/google";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-sans"
});

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-serif"
});

export const metadata: Metadata = {
  title: "Document Intelligence Platform",
  description: "AI-powered platform for scraping, retrieval, and Q&A over books"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${fraunces.variable}`}>
      <body className="font-[var(--font-sans)]">
        <main className="mx-auto min-h-screen max-w-6xl px-4 py-8 md:px-8">{children}</main>
      </body>
    </html>
  );
}
