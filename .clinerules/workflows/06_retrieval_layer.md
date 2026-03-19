# Retrieval Layer Workflow

## Goal
Implement hybrid retrieval for the local MVP.

## Product Requirement
Retrieval must not rely on embeddings only.

## Files

### `app/retrieval/search.py`
Responsibilities:
- expose top-level retrieval API,
- accept user query,
- request dense retrieval,
- request lexical retrieval,
- combine candidates,
- return final ranked chunk list.

### `app/retrieval/hybrid.py`
Responsibilities:
- implement hybrid retrieval merge logic,
- perform reciprocal rank fusion or weighted score merge,
- deduplicate candidates by chunk_id,
- preserve score components for explainability.

### `app/retrieval/rerank.py`
Responsibilities:
- perform lightweight reranking suitable for MVP,
- optionally reweight results using:
  - exact term overlap,
  - title overlap,
  - source type preferences,
  - chunk length sanity.

Requirement:
- keep reranking lightweight for laptop execution.

### `app/retrieval/thresholds.py`
Responsibilities:
- define evidence thresholds,
- determine when retrieval is weak,
- determine when to trigger fallback,
- evaluate whether enough support exists for generation.

## Retrieval Strategy

### Dense Retrieval
- embed user query with Ollama embedding model,
- retrieve semantic matches from Qdrant.

### Lexical Retrieval
For MVP, acceptable options:
- metadata/title overlap scoring in application layer,
- lightweight local lexical search side index,
- or Qdrant-supported hybrid sparse route if implemented.

### Fusion
- merge dense and lexical candidates,
- keep top candidate set,
- apply lightweight rerank,
- return top 6 to 8 chunks for generation.

## Required Output
For each final candidate include:
- chunk_id
- doc_id
- text
- title
- url
- source_type
- dense_score
- lexical_score
- fused_score

## Fallback Conditions
Trigger fallback if:
- no relevant candidates,
- scores below threshold,
- weak overlap with user query,
- contradictory evidence without resolution.

## Deliverable
Implement one retrieval entry point that returns ranked, source-aware evidence chunks.