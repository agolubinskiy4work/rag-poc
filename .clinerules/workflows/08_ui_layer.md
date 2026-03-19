# UI Layer Workflow

## Goal
Design the Streamlit interface for manual sync and chat.

## File

### `app/ui/streamlit_app.py`

## Main Responsibilities
- render the full app,
- accept source URLs,
- accept uploaded files,
- trigger Sync / Reindex,
- display sync progress,
- render chat interface,
- show answer and sources,
- show fallback messaging.

## UI Layout

### Sidebar
Components:
- text area for URLs
- file uploader
- Sync / Reindex button
- settings:
  - generator model
  - embedding model
  - retrieval top-k
  - rerank on/off

### Main Area
Components:
- title and app description
- chat history
- chat input
- answer panel
- source citations section
- confidence / fallback message

## Sync UX
When user clicks Sync / Reindex:
- show progress status,
- show per-item result if possible,
- show final summary:
  - indexed count
  - skipped count
  - failed count

## Chat UX
When user asks a question:
- show user message,
- show assistant response,
- show sources under the answer,
- show fallback clearly if the system does not know.

## Requirements
- clean and minimal UI,
- local-only usage,
- no authentication,
- no background sync states.

## Deliverable
Implement a single Streamlit entrypoint that wires together sync and chat flows.