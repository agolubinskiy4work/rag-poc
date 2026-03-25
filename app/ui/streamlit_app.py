"""Single Streamlit entrypoint wiring sync and chat flows."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import requests

from app.shared.config import SETTINGS
from app.shared.logging_utils import configure_logging


def _post_json(path: str, payload: dict) -> dict:
    base_url = SETTINGS.api_base_url.rstrip("/")
    response = requests.post(f"{base_url}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def _parse_urls(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def _save_uploaded_file(upload) -> Path:
    SETTINGS.uploads_dir.mkdir(parents=True, exist_ok=True)
    destination = SETTINGS.uploads_dir / upload.name
    destination.write_bytes(upload.getbuffer())
    return destination


def main() -> None:
    configure_logging(SETTINGS.logs_dir)

    logo_path = Path(__file__).resolve().parent / "assets" / "rag_icon.png"

    st.set_page_config(page_title="IAM Local RAG", layout="wide")
    st.title("IAM Local Knowledge Assistant (MVP)")
    st.caption("Local-only RAG with Ollama + Qdrant + Streamlit")

    with st.sidebar:
        if logo_path.exists():
            _, logo_col, _ = st.columns([1, 2, 1])
            with logo_col:
                st.image(str(logo_path), use_container_width=True)

        st.subheader("Sources")
        raw_urls = st.text_area("URLs (one per line)", height=120)
        uploads = st.file_uploader(
            "Upload .txt/.md transcripts",
            type=["txt", "md"],
            accept_multiple_files=True,
        )
        st.divider()
        st.subheader("Runtime settings")
        st.caption(f"Generator model: {SETTINGS.generation_model}")
        st.caption(f"Embedding model: {SETTINGS.embedding_model}")
        st.caption(f"Top-k: {SETTINGS.final_top_k}")

        sync_clicked = st.button("Sync / Reindex", type="primary")

    if sync_clicked:
        with st.spinner("Running sync..."):
            source_inputs: list[dict[str, str | None]] = []
            for url in _parse_urls(raw_urls):
                source_inputs.append({"source_type": "url", "value": url, "file_name": None})
            for upload in uploads or []:
                path = _save_uploaded_file(upload)
                source_inputs.append({"source_type": "file", "value": str(path), "file_name": upload.name})

            if not source_inputs:
                st.warning("Please provide at least one URL or file to sync.")
            else:
                try:
                    result = _post_json("/api/sync", {"sources": source_inputs})
                except requests.RequestException as exc:
                    st.error(f"Sync request failed: {exc}")
                else:
                    st.success("Sync completed")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total", result.get("total_sources", 0))
                    col2.metric("Indexed", result.get("indexed_count", 0))
                    col3.metric("Skipped", result.get("skipped_count", 0))
                    col4.metric("Failed", result.get("failed_count", 0))
                    for item in result.get("items", []):
                        st.write(
                            f"- **{str(item.get('status', 'unknown')).upper()}** "
                            f"`{item.get('source_ref', '')}`: {item.get('message', '')}"
                        )

    st.divider()
    st.subheader("Chat")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question about indexed sources...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving and generating..."):
                try:
                    answer_payload = _post_json("/api/chat", {"question": question})
                except requests.RequestException as exc:
                    st.error(f"Chat request failed: {exc}")
                    return

            st.markdown(answer_payload.get("answer_text", ""))
            st.markdown(f"**Confidence:** {answer_payload.get('confidence', 'Unknown')}")
            if answer_payload.get("fallback_used") and answer_payload.get("fallback_reason"):
                st.warning(f"Fallback reason: {answer_payload.get('fallback_reason')}")

            st.markdown("### Sources")
            citations = answer_payload.get("citations", [])
            if not citations:
                st.write("No sources available.")
            for citation in citations:
                st.markdown(f"- **{citation.get('title', 'Untitled')}** ({citation.get('url_or_path', '')})")
                if citation.get("section_title"):
                    st.caption(f"Section: {citation.get('section_title')}")
                st.caption(citation.get("snippet", ""))

            assistant_text = (
                f"{answer_payload.get('answer_text', '')}\n\n"
                f"Confidence: {answer_payload.get('confidence', 'Unknown')}"
            )
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})


if __name__ == "__main__":
    main()
