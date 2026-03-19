# Shared Layer Workflow

## Goal
Define shared modules, common schemas, config, and utility responsibilities.

## Files

### `app/shared/config.py`
Responsibilities:
- load environment variables,
- define application settings,
- expose values such as:
  - Ollama base URL
  - Ollama model names
  - Qdrant host/port
  - collection name
  - chunk size
  - chunk overlap
  - retrieval top-k
  - rerank limits
  - score thresholds
  - local data paths

Requirements:
- use a clear configuration object,
- keep defaults suitable for local MVP,
- allow `.env` overrides.

### `app/shared/schemas.py`
Responsibilities:
- define common dataclasses or Pydantic models for:
  - SourceInput
  - DocumentRecord
  - ChunkRecord
  - SyncResult
  - RetrievalCandidate
  - AnswerPayload
  - SourceCitation

Requirements:
- use strong typed models,
- keep schemas reusable across modules,
- include metadata fields needed for source attribution.

### `app/shared/logging_utils.py`
Responsibilities:
- configure logging,
- standardize log format,
- provide helper functions for module loggers,
- log sync status, retrieval decisions, and generation fallback reasons.

### `app/shared/utils.py`
Responsibilities:
- reusable helper functions,
- text normalization helpers,
- hash helpers,
- timestamp helpers,
- list dedup helpers,
- safe truncation helpers.

## Required Shared Models

### DocumentRecord
Fields:
- doc_id
- source_type
- title
- url
- file_name
- content_type
- clean_text
- document_hash
- indexed_at
- metadata

### ChunkRecord
Fields:
- chunk_id
- doc_id
- chunk_index
- text
- title
- url
- source_type
- section_title
- token_count
- document_hash

### RetrievalCandidate
Fields:
- chunk_id
- doc_id
- text
- title
- url
- source_type
- dense_score
- lexical_score
- fused_score
- rank

### SourceCitation
Fields:
- title
- url_or_path
- section_title
- snippet

### AnswerPayload
Fields:
- answer_text
- confidence
- fallback_used
- fallback_reason
- citations
- used_chunk_ids

## Deliverable
Implement reusable shared models before module-specific logic.