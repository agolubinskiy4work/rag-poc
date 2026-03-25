# Local RAG MVP (Ollama + Qdrant + FastAPI + Streamlit)

Local-only retrieval-augmented assistant for indexing URLs/files and answering grounded questions with citations.

## How it works (high level)

This project is a minimal, local-only **RAG (Retrieval-Augmented Generation)** pipeline.

### Components

- **FastAPI backend** (`app/api/main.py`): exposes health, sync, chat, and page-aware chat HTTP endpoints.
- **Streamlit UI** (`app/ui/streamlit_app.py`): optional UI client that calls the backend over HTTP.
- **Ingestion pipeline** (`app/ingest/*`): fetches content (URL/file), parses it, cleans it, and splits it into chunks.
- **Embeddings** (`app/indexing/embeddings.py`): uses **Ollama** to turn each chunk (and each query) into a vector.
- **Vector store (Qdrant)** (`app/indexing/qdrant_store.py`): stores vectors and performs similarity search.
- **Metadata store (SQLite)** (`app/storage/metadata_db.py`): stores bookkeeping data about sources/documents/sync runs.
- **Retrieval** (`app/retrieval/search.py` + helpers): finds relevant chunks for a question using dense + lexical + fusion.
- **Generation** (`app/generation/*`): calls Ollama to produce a grounded answer with citations.

### Indexing flow (Sync / Reindex)

1. You provide **sources** (URLs and/or uploaded `.txt` / `.md` files).
2. The ingestion layer **fetches + parses** the source into text.
3. Text is **cleaned** and **chunked** (configurable `CHUNK_SIZE` / `CHUNK_OVERLAP`).
4. Each chunk is embedded via Ollama into a numeric vector.
5. Chunks are upserted into **Qdrant** with a payload containing `doc_id`, `chunk_id`, `text`, `title`, `url`, etc.
6. **SQLite** is updated with metadata about what was indexed, skipped, or failed.

### Question-answering flow

1. Your question is embedded (Ollama embedding model).
2. **Dense retrieval**: query Qdrant for the nearest vectors (cosine similarity).
3. **Lexical retrieval (small datasets)**: the app also computes a simple token-overlap score by scanning stored chunks.
4. Dense + lexical candidates are **fused**, optionally **reranked**, and checked against **evidence thresholds**.
5. The top chunks are placed into a prompt as **context**, and the generator model answers with citations.

## Qdrant and SQL

- **SQL databases** (SQLite/Postgres/etc.) are designed for *structured data* (rows/columns) and queries like joins,
  filters, aggregates, and transactions.
- **Qdrant** is a *vector database*: it is designed for fast **similarity search** over embedding vectors
  ("find chunks that are semantically closest to this question").

This project uses both:

- **SQLite** (`data/cache/metadata.db`) for metadata and sync bookkeeping.
- **Qdrant** for storing and searching chunk vectors efficiently.

In tiny demos you could store vectors in a SQL database, but efficient nearest-neighbor search typically requires
specialized indexing (e.g. `pgvector` in Postgres). For a local MVP, Qdrant is a simple and robust choice.

## Installation

1. Ensure local services are running:
   - Ollama (default: `http://localhost:11434`)
   - Qdrant (default: `localhost:6333`)
2. Start Qdrant with Docker Compose:

```bash
docker compose up -d qdrant
```

3. Verify Qdrant is healthy:

```bash
curl http://localhost:6333/healthz
```

Expected response:

```json
{"title":"qdrant - vector search engine"}
```

4. Use the existing virtual environment and install dependencies:

```bash
./.venv/bin/pip install -r requirements.txt
```

## Configuration

Set values in `.env` (optional). Defaults are in `app/shared/config.py`.

Important variables:
- `OLLAMA_BASE_URL`
- `EMBEDDING_MODEL`
- `GENERATION_MODEL`
- `QDRANT_HOST`
- `QDRANT_PORT`
- `QDRANT_COLLECTION`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`
- `API_HOST` (default: `127.0.0.1`)
- `API_PORT` (default: `8000`)
- `API_BASE_URL` (default: `http://127.0.0.1:8000`)
- `API_CORS_ORIGINS` (default: `http://localhost:8501`)

For this Docker Compose setup, if you run the app on your host machine, keep:
- `QDRANT_HOST=localhost`
- `QDRANT_PORT=6333`

## How to run

```bash
./run.sh
```

This starts:
- FastAPI at `http://127.0.0.1:8000`
- Streamlit at `http://localhost:8501`

Or run backend only:

```bash
./.venv/bin/uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

## API endpoints (MVP)

- `GET /health`
- `POST /api/sync`
- `POST /api/chat`
- `POST /api/chat/page`

### Example: health

```bash
curl http://127.0.0.1:8000/health
```

### Example: index documents

```bash
curl -X POST http://127.0.0.1:8000/api/sync \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"source_type": "url", "value": "https://example.com"}
    ]
  }'
```

### Example: query indexed knowledge

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this source about?"}'
```

### Example: page-aware chat

```bash
curl -X POST http://127.0.0.1:8000/api/chat/page \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Summarize the current page",
    "page_url": "https://example.com",
    "page_html": "<html><body><h1>Example</h1></body></html>"
  }'
```

## How to index documents

1. Open the app.
2. In sidebar, add URLs (one per line) and/or upload `.txt` / `.md` files.
3. Click **Sync / Reindex**.
4. Review summary counts: indexed/skipped/failed.

## Example queries

- "What are the key requirements for the ingestion layer?"
- "Summarize fallback behavior rules."
- "Which sources mention retrieval thresholds?"

## Notes

- All inference is local via Ollama.
- Metadata is stored in SQLite (`data/cache/metadata.db`).
- Vectors are stored in Qdrant.
- Qdrant data is persisted in the Docker volume `qdrant_storage`.

## Docker Compose quick commands

Start Qdrant:

```bash
docker compose up -d qdrant
```

Stop Qdrant:

```bash
docker compose stop qdrant
```

Remove Qdrant container (keep data volume):

```bash
docker compose rm -f qdrant
```

Remove Qdrant + all persisted vector data:

```bash
docker compose down -v
```

