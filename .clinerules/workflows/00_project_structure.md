# Project Structure Workflow

## Goal
Define the folder structure and responsibilities for a local MVP RAG assistant.

## Product Constraints
- Local-only
- Runs on MacBook M3 Pro
- Python project
- Streamlit UI
- Ollama for local embeddings and generation
- Qdrant for retrieval storage
- Manual ingestion only through UI button
- No background workers
- No testing required for this workflow pack

## Target Folder Structure

```text
rag-poc/
├── app/
│   ├── ui/
│   ├── ingest/
│   ├── indexing/
│   ├── retrieval/
│   ├── generation/
│   ├── storage/
│   └── shared/
├── data/
│   ├── uploads/
│   ├── cache/
│   └── logs/
├── workflows/
├── requirements.txt
├── .env
├── README.md
└── run.sh
```

## Folder Responsibilities

app/ui/

Contains the Streamlit application and all UI-level orchestration.

app/ingest/

Contains source fetching, file reading, HTML parsing, content cleaning, and chunking logic.

app/indexing/

Contains embedding generation, Qdrant write operations, deduplication, and sync orchestration.

app/retrieval/

Contains dense retrieval, lexical retrieval, hybrid fusion, reranking, and fallback thresholds.

app/generation/

Contains Ollama generation client, prompts, and final answer formatting.

app/storage/

Contains local metadata persistence and document/chunk repositories.

app/shared/

Contains config, shared schemas, utility helpers, and logging helpers.

data/uploads/

Stores uploaded files if the app persists them locally before indexing.

data/cache/

Stores temporary fetched content, intermediate parsed files, or reusable cache artifacts.

data/logs/

Stores application logs and sync logs.

workflows/

Contains planning markdown files used by Cline Plan Mode.

## Deliverable

Create the full folder structure first before implementing internal modules