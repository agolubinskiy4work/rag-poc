# Workflow 15 — Violentmonkey Sidebar AI Assistant (Page + Index RAG)

## Goal

Implement a Violentmonkey userscript that injects a right-side AI assistant on configured URLs.

The sidebar should be intentionally simple:
- logo,
- chat messages,
- input + send.

On each user question, the script sends page context to backend. Backend answers using:
1) relevant information extracted from the current page,
2) and additional knowledge from indexed sources.

---

## 1. UX Requirements (Sidebar)

## Placement
- fixed panel on the right side,
- overlays the current page,
- can be collapsed/expanded.

## Minimal UI elements
- logo area,
- chat history area,
- one text input,
- one send button.

No extra controls are required for MVP.

---

## 2. URL Targeting

Userscript must support configurable match patterns.

Requirement:
- list of URL patterns is parameterized in variables at top of script,
- supports multiple patterns,
- easy to edit later without changing core logic.

---

## 3. Browser → Backend Request Contract

For each user message, send payload to backend endpoint (`/api/chat/page`):

- `question`: user chat text,
- `page_url`: current `window.location.href`,
- `page_html`: full HTML (`document.documentElement.outerHTML`),
- optional metadata: page title, timestamp.

Transport:
- `POST` JSON,
- backend URL configurable via script variable (e.g. `http://127.0.0.1:8000`).

---

## 4. Backend Processing Flow (Page-Aware RAG)

Endpoint receives `question + page_url + page_html`.

Processing sequence:

1. Parse HTML safely.
2. Extract readable text from page body.
3. Extract relevant links/URLs from the page (same-site links preferred).
4. Build temporary page-derived context chunks.
5. Retrieve index-based candidates from Qdrant/metadata using existing retrieval pipeline.
6. Fuse page-derived candidates + indexed candidates.
7. Apply evidence checks / reranking.
8. Generate final answer via Ollama.
9. Return answer with clickable references.

---

## 5. Parsing Requirements (Server)

Input is raw HTML; backend must parse it and avoid noisy content.

MVP parsing requirements:
- remove scripts/styles/nav boilerplate where possible,
- keep readable text blocks,
- collect anchor links from `<a href>`,
- normalize relative links to absolute using `page_url`,
- deduplicate links,
- limit number of extracted links/chunks for performance.

Graceful behavior:
- if HTML is malformed, continue with best-effort parsing,
- if page text is empty, continue using indexed knowledge only.

---

## 6. Response Contract (Backend → Userscript)

Response must include:
- `answer_text`,
- `confidence`,
- `citations` list,
- optional `fallback_reason`.

Each citation should contain:
- `title`,
- `url_or_path` (clickable),
- `snippet`,
- optional `source_type` (`page` or `index`).

---

## 7. Citation Behavior

Assistant must provide clickable references in UI when available.

Priority:
1. relevant page URLs extracted from current site/page,
2. indexed citations from existing RAG store.

Rules:
- never fabricate links,
- only show URLs present in extracted page anchors or indexed metadata,
- if no links available, clearly state source limitation.

---

## 8. Error Handling (MVP)

Userscript must handle:
- backend unreachable,
- timeout,
- non-200 responses,
- malformed JSON response.

Backend must handle:
- missing `page_html` or `question`,
- oversized HTML payload (apply max size),
- parse failures,
- low-evidence responses (fallback mode).

---

## 9. Security / Local Constraints

- backend expected local by default,
- CORS configured to allow needed origins,
- no external AI API calls,
- no company data leaves machine.

Optional hardening later:
- local API token header,
- request size/rate limits,
- origin validation.

---

## 10. Suggested Implementation Breakdown

1. Add FastAPI endpoint `POST /api/chat/page` with request/response schemas.
2. Add server-side HTML parser helper for text + links extraction.
3. Add candidate fusion logic (page context + indexed retrieval).
4. Return unified answer payload with citations.
5. Create Violentmonkey script with:
   - configurable URL patterns,
   - right sidebar UI,
   - chat event handling,
   - API calls and rendering citations as clickable links.
6. Add brief usage section to README (how to install/import userscript).

---

## Deliverable

A working browser sidebar assistant on configured URLs that:
- sends full page HTML plus user question to local backend,
- backend extracts page knowledge and combines it with indexed RAG knowledge,
- returns grounded answers with clickable URL references.
