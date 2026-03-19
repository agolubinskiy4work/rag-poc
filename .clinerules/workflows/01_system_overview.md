# System Overview Workflow

## Goal
Describe the full MVP architecture and the responsibilities of each subsystem.

## Product Goal
Build a local internal knowledge assistant that:
- accepts questions in a Streamlit chat,
- indexes internal URLs and local transcript/text files,
- retrieves relevant chunks using hybrid retrieval,
- generates grounded answers with Ollama,
- includes source attribution,
- says "I don't know" when evidence is weak.

## High-Level Architecture

1. UI Layer
2. Ingestion Layer
3. Indexing Layer
4. Retrieval Layer
5. Generation Layer
6. Local Metadata Storage

## User Flow Summary

### Sync / Reindex Flow
1. User adds URLs and/or uploads files.
2. User clicks Sync / Reindex.
3. System fetches and parses content.
4. System cleans and chunks text.
5. System generates embeddings.
6. System writes chunks and metadata to Qdrant.
7. System stores sync metadata locally.
8. UI shows sync summary.

### Ask Flow
1. User asks a question in chat.
2. System runs hybrid retrieval.
3. System merges and reranks candidate chunks.
4. System evaluates evidence strength.
5. System either:
   - generates grounded answer with sources, or
   - returns "I don't know" with related sources.

## Non-Goals for MVP
- No scheduled sync
- No background jobs
- No auth
- No ACL/permissions
- No distributed deployment
- No external cloud inference required

## Required System Guarantees
- Retrieval must not depend on embeddings only.
- Final answer must always include sources when answer is given.
- Final answer must avoid unsupported claims.
- System must support refusal/fallback when context is weak.