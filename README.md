# Local RAG MVP (Ollama + Qdrant + Streamlit)

Local-only retrieval-augmented assistant for indexing URLs/files and answering grounded questions with citations.

## How it works (high level)

This project is a minimal, local-only **RAG (Retrieval-Augmented Generation)** pipeline.

### Components

- **Streamlit UI** (`app/ui/streamlit_app.py`): lets you add URLs/upload files, run sync/reindex, and ask questions.
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
2. Use the existing virtual environment and install dependencies:

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

## How to run

```bash
./run.sh
```

This starts Streamlit at `http://localhost:8501`.

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

