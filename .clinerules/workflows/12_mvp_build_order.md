# MVP Build Order Workflow

## Goal
Define implementation order for the MVP without tests.

## Build Order

### Step 1: Project skeleton
Create:
- folder structure
- requirements
- config loader
- shared schemas
- logging helpers

Done when:
- project structure exists,
- app imports work cleanly.

### Step 2: Storage foundation
Create:
- SQLite metadata DB
- repository helpers

Done when:
- app can store source and document metadata.

### Step 3: Ollama and Qdrant wrappers
Create:
- Ollama embedding client
- Ollama generation client
- Qdrant store wrapper

Done when:
- app can connect to local Ollama and Qdrant.

### Step 4: Ingestion pipeline
Create:
- fetcher
- parsers
- cleaner
- chunker

Done when:
- URLs and files can be converted into chunk-ready documents.

### Step 5: Sync service
Create:
- dedup logic
- manual sync orchestration
- Qdrant upsert integration

Done when:
- user-triggered sync indexes documents end-to-end.

### Step 6: Retrieval pipeline
Create:
- dense retrieval
- lexical retrieval
- hybrid fusion
- thresholds

Done when:
- app returns ranked evidence chunks for a question.

### Step 7: Generation pipeline
Create:
- prompts
- answer builder
- fallback logic

Done when:
- app returns grounded answers with sources or fallback.

### Step 8: Streamlit UI
Create:
- source input UI
- sync UI
- chat UI
- answer display
- source display

Done when:
- full MVP can be used from one Streamlit app.

## Final MVP Definition of Done
- manual sync works,
- indexed sources are retrievable,
- chat answers are grounded,
- every answer includes sources,
- weak evidence triggers fallback,
- everything runs locally on the laptop.