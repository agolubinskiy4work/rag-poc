# Workflow 14 — UI / Server Separation (FastAPI + Reusable UI)

## Goal

Separate backend logic from Streamlit so any UI client can be used (Streamlit, Violentmonkey sidebar, CLI, or future frontend).

This workflow keeps the existing MVP retrieval/generation/indexing logic, but exposes it through a clear HTTP API.

---

## 1. Why this separation

Current state:
- `app/ui/streamlit_app.py` directly calls sync and chat functions.

Target state:
- Streamlit becomes one client only.
- Backend service (FastAPI) owns business logic entrypoints.
- Other clients can call the same endpoints.

Benefits:
- reusable backend,
- easier integration with browser userscripts,
- cleaner boundaries,
- still local-only.

---

## 2. Architecture Target

## Backend (FastAPI)
New API layer should expose:
- health endpoint,
- sync/index endpoint,
- chat/query endpoint,
- page-aware chat endpoint (for browser sidebar use case).

Backend reuses existing modules:
- indexing: `app/indexing/*`
- retrieval: `app/retrieval/*`
- generation: `app/generation/*`
- storage: `app/storage/*`

## UI Clients
- Streamlit UI calls backend via HTTP.
- Violentmonkey userscript calls backend via HTTP.
- Any new UI can be added without changing core backend logic.

---

## 3. API Contracts (MVP)

## `GET /health`
Returns service status.

Response:
- service name
- status
- optional model/config info

## `POST /api/sync`
Runs sync/reindex for sources.

Request (example):
- URLs
- local file paths (if enabled)
- sync options

Response:
- total/indexed/skipped/failed
- per-source item results

## `POST /api/chat`
Standard RAG chat from indexed knowledge.

Request:
- `question`

Response:
- answer text
- confidence
- citations (title + clickable URL/path + snippet)
- fallback metadata

## `POST /api/chat/page`
Page-aware chat for browser integrations.

Request:
- `question`
- `page_url`
- `page_html`

Response:
- answer text
- confidence
- citations including clickable links
- breakdown of evidence source types (page/index)

---

## 4. Service Layer Boundary

Introduce a lightweight service layer (MVP-simple) that wraps existing functions:

- `ChatService`:
  - standard indexed QA,
  - page-aware QA orchestration.
- `SyncService`:
  - keep existing sync orchestration,
  - expose through API endpoint.

Rule:
- API routers should validate I/O and call services.
- Core retrieval/generation stays outside API router code.

---

## 5. Streamlit Role After Separation

Streamlit becomes optional UI client:
- gathers user inputs,
- sends HTTP requests to FastAPI,
- renders response.

Streamlit should not directly call low-level retrieval/indexing functions after migration.

---

## 6. Configuration Requirements

Add backend-friendly settings (env-driven):
- `API_HOST` (default `127.0.0.1`)
- `API_PORT` (default `8000`)
- `API_CORS_ORIGINS` (for local browser/userscript calls)

Keep existing local-only model setup:
- Ollama for inference,
- Qdrant for vectors,
- SQLite for metadata.

---

## 7. Security / Local MVP Constraints

For MVP:
- local network only by default,
- explicit CORS allowlist,
- no cloud calls,
- no external AI APIs,
- company data stays local.

Optional next step:
- simple API key header for non-local deployment.

---

## 8. Logging and Reliability

Backend must log:
- request start/end,
- sync summary,
- retrieval + generation timing,
- page parsing errors.

Must handle gracefully:
- malformed request payloads,
- invalid HTML,
- empty extracted page text,
- retrieval with insufficient evidence.

---

## 9. Implementation Sequence (MVP)

1. Add FastAPI app entrypoint and router skeleton.
2. Add `/health`, `/api/chat`, `/api/sync` endpoints.
3. Move Streamlit to HTTP-client mode.
4. Add `/api/chat/page` for browser assistant integration.
5. Add request/response schemas for API payloads.
6. Update `README.md` with backend run instructions.

---

## Deliverable

Backend and UI are clearly separated:
- FastAPI exposes RAG functionality via HTTP,
- Streamlit is optional UI,
- architecture supports multiple clients (including Violentmonkey sidebar) without duplicating logic.
