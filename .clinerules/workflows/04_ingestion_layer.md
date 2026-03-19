# Ingestion Layer Workflow

## Goal
Design and implement ingestion of URLs and uploaded text files.

## Scope
Supported input types:
- internal HTML pages by URL
- uploaded `.txt`
- uploaded `.md`
- transcript text files

## Files

### `app/ingest/models.py`
Responsibilities:
- define ingestion-specific intermediate models such as:
  - RawSource
  - ParsedDocument
  - ChunkingInput

### `app/ingest/fetcher.py`
Responsibilities:
- fetch HTML content from provided URLs,
- return raw response metadata,
- handle network errors,
- support local/manual sync only.

Requirements:
- no crawler behavior for MVP,
- process only explicitly provided URLs,
- store status for each fetch.

### `app/ingest/parsers.py`
Responsibilities:
- parse content by source type,
- route HTML to HTML parser,
- route text files to plain text parser,
- extract title where possible,
- output normalized parsed document object.

Requirements:
- HTML parser must preserve useful title/body structure,
- text parser must keep file name and source type.

### `app/ingest/cleaner.py`
Responsibilities:
- clean parsed HTML body,
- remove navigation, footer, sidebar, boilerplate, repeated UI chrome,
- normalize whitespace,
- preserve relevant headings and procedural text,
- prepare clean text for chunking.

Requirements:
- prioritize meaningful content extraction,
- avoid indexing menus and decorative text.

### `app/ingest/chunker.py`
Responsibilities:
- split clean text into retrieval chunks,
- preserve document metadata on each chunk,
- optionally include section headings in chunk context.

Chunking rules:
- use moderate chunk size,
- include overlap,
- avoid overly tiny chunks,
- preserve heading context if available.

## Ingestion Output
The ingestion layer must output:
- one normalized document record,
- many chunk records,
- metadata required for indexing.

## Important Requirements
- clean HTML before chunking,
- preserve source attribution fields,
- compute normalized text for hashing,
- support transcript files as first-class source type.

## Deliverable
Implement deterministic manual ingestion pipeline from raw source to chunk-ready document.