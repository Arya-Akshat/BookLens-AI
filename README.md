# AI-Powered Document Intelligence Platform

Production-ready full-stack platform for book data ingestion, retrieval, and AI-powered question answering.

## Features

- Selenium-based scraping from books.toscrape.com
- Metadata storage in Django ORM (MySQL-ready)
- Embeddings with Sentence Transformers
- Vector storage with ChromaDB (fallback memory index for dev/test resilience)
- Full RAG pipeline with contextual answers and citations
- AI insights:
  - Summary generation
  - Genre classification
  - Similar book recommendation
- REST APIs via Django REST Framework
- Next.js + Tailwind frontend:
  - Dashboard
  - Book detail + AI insights
  - Q&A interface with sources
- Django tests for upload, Q&A, and recommendation endpoints
- Sample dataset + management command loader

## Tech Stack

- Backend: Python, Django, Django REST Framework, MySQL, ChromaDB, Sentence Transformers, Selenium
- LLM Provider: LM Studio (default local), OpenAI (optional)
- Frontend: Next.js (App Router), Tailwind CSS

## Project Structure

- backend/
  - manage.py
  - requirements.txt
  - config/
  - books/
    - models.py
    - serializers.py
    - views.py
    - urls.py
    - tests.py
    - sample_data.json
    - services/
      - scraper.py
      - embeddings.py
      - rag_pipeline.py
      - ai_insights.py
- frontend/
  - app/
  - components/
  - lib/api.ts
- .env.example
- README.md

## Environment Variables

Copy .env.example to .env and update values.

Key variables:

- DB_ENGINE=django.db.backends.mysql
- MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT
- CHROMA_DB_PATH
- EMBEDDING_MODEL_NAME
- LM_STUDIO_BASE_URL
- LM_STUDIO_MODEL
- OPENAI_API_KEY (optional)
- NEXT_PUBLIC_API_BASE_URL

## Backend Setup

1. Create and activate virtual environment (optional if already created)
2. Install dependencies

   pip install -r backend/requirements.txt

3. Run migrations

   cd backend
   python manage.py migrate

4. Load sample data and embeddings

   python manage.py load_sample_data

5. Start backend server

   python manage.py runserver

Backend default URL:

- http://127.0.0.1:8000

## Frontend Setup

1. Install dependencies

   cd frontend
   npm install

2. Start development server

   npm run dev

Frontend default URL:

- http://localhost:3000

## Scraper Usage

### API trigger for scraping

POST /api/books/upload/

Body examples:

- Bulk scrape first 2 pages:

  {
    "pages": 2,
    "bulk": true
  }

- Single book scrape:

  {
    "book_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "bulk": false
  }

## API Documentation

### GET APIs

- GET /api/books/
  - List all books

- GET /api/books/<id>/
  - Get single book details + AI insights

- GET /api/books/recommend/<id>/
  - Recommend similar books

### POST APIs

- POST /api/books/upload/
  - Scrape and store books

- POST /api/ask/
  - RAG-based question answering

Request:

{
  "question": "Which books involve space politics?",
  "top_k": 5
}

Response:

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

## cURL Samples

### List books

curl -X GET http://127.0.0.1:8000/api/books/

### Book detail

curl -X GET http://127.0.0.1:8000/api/books/1/

### Recommendations

curl -X GET http://127.0.0.1:8000/api/books/recommend/1/

### Upload scrape (bulk)

curl -X POST http://127.0.0.1:8000/api/books/upload/ \
  -H "Content-Type: application/json" \
  -d '{"pages":1,"bulk":true}'

### Ask RAG question

curl -X POST http://127.0.0.1:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question":"Which fantasy books are hero journeys?","top_k":5}'

## Postman Collection Tips

- Set base URL variable: http://127.0.0.1:8000
- Add requests for the 5 endpoints above
- Use JSON body for upload and ask endpoints

## Testing

Run Django tests:

cd backend
python manage.py test

Included tests:

- Book upload API test
- Q&A endpoint test
- Recommendation API test

## Sample Q&A

Question:

- Which books discuss political conflict in a futuristic setting?

Expected grounded answer:

- Dune is likely returned with citation from its embedded description chunk.

## Screenshots

Add screenshots after running locally:

- docs/screenshots/dashboard.png
- docs/screenshots/book-detail.png
- docs/screenshots/rag-qa.png

## Notes on MySQL

- This project is configured for MySQL via environment settings.
- For local quick-start, SQLite fallback is automatic if DB_ENGINE is not set to MySQL.

## Extra Features Included

- Basic async scraping flow with ThreadPoolExecutor for save+embed processing
- Bulk scraping support via pages parameter
- Caching for summaries and RAG responses
