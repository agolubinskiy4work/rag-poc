# End-to-End Chat Flow Workflow

## Goal
Describe the full question-answering sequence for the Streamlit chat.

## Entry Point
Triggered when user submits a chat message.

## Flow

1. Receive user question.
2. Normalize question string.
3. Generate query embedding.
4. Run dense retrieval.
5. Run lexical retrieval.
6. Fuse candidate lists.
7. Apply lightweight reranking.
8. Evaluate evidence thresholds.
9. If evidence is sufficient:
   - build generation prompt,
   - include top chunks and source metadata,
   - call Ollama generation,
   - format answer,
   - attach source citations,
   - return final payload to UI.
10. If evidence is insufficient:
   - return fallback response,
   - optionally show related sources,
   - mark confidence as insufficient evidence.

## Required Chat Output
- answer text
- confidence level
- sources
- fallback reason if used

## Required Behavior
- no unsupported claims,
- no fabricated source details,
- no answer without supporting evidence.

## Deliverable
Implement chat pipeline as a retrieval-first, evidence-aware flow.