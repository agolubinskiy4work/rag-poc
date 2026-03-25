# Workflow 13 — Confluence Web Ingestor

## Goal

Design and implement a Confluence web ingestor for the local MVP RAG assistant.

This workflow must use the architectural context defined in `00_master_workflow.md`.

The ingestor must:
- accept one or more Confluence page URLs as input,
- open and parse the provided pages over HTTP,
- extract clean page content,
- follow internal Confluence links up to a configurable `depth`,
- index all discovered pages,
- store page title and canonical page URL in the local metadata database,
- and make those URLs available later for source attribution in chat answers.

This workflow is intentionally **web-ingestion-first**, not API-first.

---

# 1. Core Requirements

## Functional Requirements
The Confluence web ingestor must:
- accept a starting URL or a list of starting URLs,
- fetch the HTML of each page,
- extract meaningful page content,
- detect and follow internal Confluence page links,
- stop traversal at a configurable depth,
- avoid revisiting the same page,
- chunk and index page content,
- store source metadata locally,
- preserve page title and original URL for later answer citations.

## Non-Functional Requirements
- local-only execution,
- manual trigger only through the existing Sync / Reindex flow,
- no background crawling,
- no infinite traversal,
- no external browser automation unless clearly needed,
- deterministic and bounded crawling.

---

# 2. Depth Semantics

The ingestor must support a `depth` parameter.

## Required meaning of `depth`

### `depth = 1`
Process only the starting page itself.

### `depth = 2`
Process:
- the starting page,
- and all eligible linked Confluence pages found on that page.

### `depth = 3`
Process:
- the starting page,
- linked pages found on that page,
- and linked pages found on those second-level pages.

### General rule
For a starting page:
- level 1 = root page,
- level 2 = links from root,
- level 3 = links from level 2,
- etc.

Traversal must stop once the maximum depth is reached.

---

# 3. Crawl Boundaries

The crawler must be constrained.

## Allowed links
The ingestor should only follow:
- links that belong to the same Confluence instance or allowed host,
- links that represent actual Confluence content pages,
- links that pass optional allowlist rules.

## Disallowed links
The ingestor should not follow:
- external websites,
- logout/login/admin pages,
- attachment download links unless explicitly supported later,
- profile/help/settings pages,
- non-content utility pages,
- anchor-only links,
- duplicate URLs already visited.

## Optional configurable constraints
The design should allow support for:
- allowed hostnames
- allowed path prefixes
- max pages per run
- exclude path patterns
- include path patterns

---

# 4. Input Contract

## Input Parameters
The ingestor must support the following inputs:

- `start_urls: list[str]`
- `depth: int`
- `allowed_domains: list[str]` or inferred from start URL
- `max_pages: int`
- `follow_only_confluence_paths: bool`
- `exclude_patterns: list[str]`
- `include_patterns: list[str]`
- optional request headers / cookies / auth data if needed for internal access

## Minimum valid input
At minimum:
- one start URL
- one depth value

---

# 5. Output Contract

For each successfully processed page, the ingestor must produce:

## Document-level metadata
- `doc_id`
- `source_type = "confluence_web"`
- `title`
- `url`
- `canonical_url` if resolved
- `document_hash`
- `content_type = "text/html"`
- `crawl_depth`
- `parent_url` if discovered from another page
- `indexed_at`

## Chunk-level metadata
- `chunk_id`
- `doc_id`
- `chunk_index`
- `text`
- `title`
- `url`
- `source_type`
- `section_title` if available
- `document_hash`

This metadata must later support source attribution in chat answers.

---

# 6. Proposed File Responsibilities

## `app/ingest/fetcher.py`
Responsibilities:
- fetch raw HTML for a given Confluence page URL,
- support headers/cookies/session if needed,
- return response metadata,
- handle HTTP failures cleanly.

## `app/ingest/parsers.py`
Responsibilities:
- parse HTML into structured content,
- extract page title,
- extract main content body,
- extract candidate internal links from the page.

## `app/ingest/cleaner.py`
Responsibilities:
- remove Confluence navigation chrome,
- remove sidebar/header/footer/breadcrumb clutter,
- preserve useful page body text,
- preserve headings and procedural content,
- normalize whitespace.

## `app/ingest/chunker.py`
Responsibilities:
- split cleaned page text into chunks,
- preserve source metadata,
- optionally include section heading context.

## `app/indexing/sync_service.py`
Responsibilities:
- orchestrate the full crawl + index flow,
- manage traversal queue,
- enforce depth and limits,
- call parsing, cleaning, chunking, embedding, and indexing,
- return summary to the UI.

## `app/storage/repositories.py`
Responsibilities:
- store document metadata,
- store page title and URL,
- store crawl relationships if useful,
- store sync results.

---

# 7. Crawl Algorithm

## Recommended traversal strategy
Use either:
- BFS for clearer depth control, or
- DFS with explicit depth tracking.

For this MVP, BFS is preferable because it maps cleanly to the `depth` concept.

## Required crawler state
The crawler should maintain:
- `queue`
- `visited_urls`
- `discovered_urls`
- `current_depth`
- `page_count`
- `parent_child_relationships` optionally

## BFS traversal rules
1. enqueue all start URLs at depth 1
2. pop next URL
3. skip if already visited
4. fetch HTML
5. parse title, content, and links
6. clean content
7. hash normalized content
8. skip indexing if unchanged
9. chunk and index if needed
10. if current depth < max depth:
   - normalize discovered links
   - filter eligible Confluence links
   - enqueue new links with depth + 1
11. continue until queue empty or `max_pages` reached

---

# 8. Link Extraction Rules

The parser must extract hyperlinks from the page and normalize them.

## Required normalization
- resolve relative links to absolute URLs
- remove fragments
- normalize duplicate query variants where appropriate
- preserve canonical page URL if identifiable

## Link eligibility rules
A discovered link is eligible for follow-up if:
- it belongs to the same allowed domain,
- it appears to be a Confluence content page,
- it is not already visited,
- it is not excluded by filters.

## Deduplication rule
Two URLs that resolve to the same normalized canonical page must be treated as the same page.

---

# 9. Indexing Requirements

The crawler does not index raw HTML directly.

For every eligible page:
1. fetch HTML
2. parse title/body/links
3. clean body text
4. hash normalized content
5. compare with stored hash
6. skip unchanged pages
7. chunk cleaned text
8. embed chunks
9. upsert into Qdrant
10. update metadata DB

The stored metadata must include:
- page title
- original URL
- canonical URL if resolved
- source type
- crawl depth

---

# 10. Metadata and Source Attribution

## Local metadata database must store
- `doc_id`
- `title`
- `url`
- `canonical_url`
- `source_type`
- `document_hash`
- `indexed_at`
- `crawl_depth`

## Chat source attribution must later use
- page title
- canonical URL if available, otherwise original URL

Example source display:
- `Runbook: Restarting Service A — https://company.atlassian.net/wiki/...`

The system must preserve source URLs reliably so the chat answer can show clickable links.

---

# 11. Error Handling

The ingestor must support partial success.

## Required behavior
- one failed page must not fail the entire sync run
- failed pages must be logged and reported
- pages with empty extracted content should be marked accordingly
- unauthorized pages should be reported clearly
- redirect loops and repeated fetch failures must be bounded

## Sync summary must include
- total discovered pages
- indexed pages
- skipped unchanged pages
- failed pages
- pages excluded by filters
- max depth reached
- max pages reached if applicable

---

# 12. Safety and Crawl Limits

To keep the MVP controlled, the crawler must enforce limits.

## Required limits
- `depth`
- `max_pages`
- `visited_urls` deduplication

## Recommended MVP defaults
- `depth = 1`
- `max_pages = 50`

These defaults prevent accidental large crawls.

---

# 13. UI Integration Requirements

The existing Streamlit UI should support Confluence web ingestion with:

- text area for start URLs
- numeric input for `depth`
- numeric input for `max_pages`
- optional include/exclude patterns
- Sync / Reindex button
- sync result summary

Example UI inputs:
- Start URL: `https://company.atlassian.net/wiki/spaces/OPS/pages/...`
- Depth: `2`
- Max pages: `25`

---

# 14. Integration with Existing MVP Architecture

This workflow must integrate into the existing architecture from `00_master_workflow.md`.

## Expected integration path
- UI collects Confluence start URL(s) and crawl parameters
- sync service starts crawl
- crawler fetches + parses pages
- ingestion outputs normalized documents/chunks
- indexing layer embeds + stores chunks in Qdrant
- storage layer saves page metadata
- chat later retrieves chunks and cites stored URLs

---

# 15. Deliverable

Design and implement a Confluence web ingestor that:
- starts from user-provided Confluence page URLs,
- traverses linked Confluence pages up to a bounded depth,
- indexes clean page content,
- stores page title and URL in metadata storage,
- and enables source-linked answers in the chat UI.

The implementation must remain MVP-friendly, deterministic, and suitable for local execution.