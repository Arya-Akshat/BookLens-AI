# Document Intelligence Platform

This project is my full-stack assignment submission for a document intelligence workflow over book data. It scrapes books, stores metadata, builds embeddings, and answers grounded questions with source citations.

## What This App Does

- Scrapes books from books.toscrape.com using Selenium
- Stores metadata in Django models (MySQL-ready, SQLite-friendly for local runs)
- Creates vector embeddings for retrieval (ChromaDB with resilient in-memory fallback)
- Runs a full RAG pipeline for question answering with citations
- Generates book insights (summary + genre + recommendation logic)
- Exposes REST APIs with Django REST Framework
- Provides a Next.js + Tailwind frontend for listing, detail, and Q&A

## Assignment Checklist Coverage

- Backend GET APIs:
  - `GET /api/books/` list books
  - `GET /api/books/<id>/` full detail + AI insights
  - `GET /api/books/recommend/<id>/` related books
- Backend POST APIs:
  - `POST /api/books/upload/` scrape/process books
  - `POST /api/ask/` RAG query endpoint
- Required frontend pages:
  - Dashboard / book listing
  - Book detail page
  - Q&A interface
- AI insights included (at least 2 required):
  - Summary generation
  - Genre classification
  - Recommendation logic

## Tech Stack

- Backend: Python, Django, Django REST Framework
- Database: MySQL (configurable), SQLite (local default)
- Vector DB: ChromaDB
- Embeddings: Sentence Transformers
- LLM: LM Studio (primary), OpenAI/Groq (optional)
- Frontend: Next.js (App Router), Tailwind CSS
- Automation: Selenium

## Project Structure

```text
backend/
  manage.py
  requirements.txt
  config/
  books/
    models.py
    serializers.py
    views.py
    urls.py
    tests.py
    sample_data.json
    services/
      scraper.py
      embeddings.py
      rag_pipeline.py
      ai_insights.py
frontend/
  app/
  components/
  lib/api.ts
books/
  *.pdf
.env.example
README.md
```

## Setup Instructions

### 1) Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py load_sample_data
python manage.py runserver
```

Backend URL: `http://127.0.0.1:8000`

### Optional: Build Data + Vector Store From `books/` PDFs

The repository includes a `books/` folder with sample PDF files for testing retrieval and RAG flows.

To ingest those PDFs into the `Book` table and rebuild the Chroma vector store:

```bash
cd backend
python manage.py ingest_pdfs --source-dir ../books
```

Notes:

- This command extracts text from PDFs, creates/updates book rows, and rebuilds embeddings.
- By default, it replaces existing rows first.
- To keep existing DB rows and add PDFs on top:

```bash
cd backend
python manage.py ingest_pdfs --source-dir ../books --keep-existing
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:3000`

## Environment Variables

Copy `.env.example` to `.env` and adjust values if needed.

Important keys:

- `DB_ENGINE`
- `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`
- `CHROMA_DB_PATH`
- `EMBEDDING_MODEL_NAME`
- `LM_STUDIO_BASE_URL`, `LM_STUDIO_MODEL`
- `OPENAI_API_KEY` (optional)
- `GROQ_API_KEY` (optional)
- `NEXT_PUBLIC_API_BASE_URL`

## API Documentation

### GET Endpoints

- `GET /api/books/`: List all books
- `GET /api/books/<id>/`: Get a single book with AI insights
- `GET /api/books/recommend/<id>/`: Get related book recommendations

### POST Endpoints

- `POST /api/books/upload/`: Scrape and ingest books
- `POST /api/ask/`: Ask a retrieval-grounded question

### `POST /api/books/upload/` example payloads

Bulk scrape first 2 pages:

```json
{
  "pages": 2,
  "bulk": true
}
```

Single book scrape:

```json
{
  "book_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "bulk": false
}
```

### `POST /api/ask/` request/response

Request:

```json
{
  "question": "Which books involve space politics?",
  "top_k": 5
}
```

Response:

```json
{
  "question": "Which books involve space politics?",
  "answer": "Dune prominently explores space politics and imperial conflict [1].",
  "sources": [
    {
      "book_id": 2,
      "title": "Dune",
      "author": "Frank Herbert",
      "book_url": "https://example.com/books/dune"
    }
  ],
  "citations": ["[1]"]
}
```

## cURL Samples

```bash
curl -X GET http://127.0.0.1:8000/api/books/
curl -X GET http://127.0.0.1:8000/api/books/1/
curl -X GET http://127.0.0.1:8000/api/books/recommend/1/

curl -X POST http://127.0.0.1:8000/api/books/upload/ \
  -H "Content-Type: application/json" \
  -d '{"pages":1,"bulk":true}'

curl -X POST http://127.0.0.1:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question":"Which fantasy books are hero journeys?","top_k":5}'
```

## Sample Questions and Answers

Question:

- Which books discuss political conflict in a futuristic setting?

Typical grounded answer:

- Dune is returned with citation markers from retrieved context chunks.

## Screenshots (UI)

### Dashboard

![Dashboard](<images/Screenshot 2026-04-18 at 2.02.46 PM.png>)

### Book Detail

![Book Detail](<images/Screenshot 2026-04-18 at 2.02.53 PM.png>)

### Q&A Interface

![Q&A Interface](<images/Screenshot 2026-04-18 at 2.03.01 PM.png>)

### Recommendations / Insight View

![Recommendations](<images/Screenshot 2026-04-18 at 2.05.56 PM.png>)

### Additional UI View

![Additional UI View](<images/Screenshot 2026-04-18 at 2.06.09 PM.png>)

## Testing

Run backend tests:

```bash
cd backend
python manage.py test
```

If MySQL is not running locally:

```bash
cd backend
DB_ENGINE=django.db.backends.sqlite3 python manage.py test
```

Included tests:

- Book upload API
- Q&A endpoint
- Recommendation endpoint

## Extra Work Included

- Caching for summaries and RAG responses
- Chunk size/overlap controls for embeddings
- Async-style parallel save/embed flow using `ThreadPoolExecutor` for multi-item ingest
- Bulk scraping with configurable page count
