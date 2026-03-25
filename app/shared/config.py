"""Application configuration for local MVP RAG assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # Optional dependency for local convenience.
    pass


def _get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = _get_env("OLLAMA_BASE_URL", "http://localhost:11434")
    embedding_model: str = _get_env("EMBEDDING_MODEL", "nomic-embed-text")
    generation_model: str = _get_env("GENERATION_MODEL", "llama3.1:8b")

    qdrant_host: str = _get_env("QDRANT_HOST", "localhost")
    qdrant_port: int = _get_env_int("QDRANT_PORT", 6333)
    qdrant_collection: str = _get_env("QDRANT_COLLECTION", "rag_chunks")
    embedding_dim: int = _get_env_int("EMBEDDING_DIM", 768)

    chunk_size: int = _get_env_int("CHUNK_SIZE", 1200)
    chunk_overlap: int = _get_env_int("CHUNK_OVERLAP", 200)

    dense_top_k: int = _get_env_int("DENSE_TOP_K", 12)
    lexical_top_k: int = _get_env_int("LEXICAL_TOP_K", 12)
    final_top_k: int = _get_env_int("FINAL_TOP_K", 8)
    min_fused_score: float = _get_env_float("MIN_FUSED_SCORE", 0.08)
    min_term_overlap: int = _get_env_int("MIN_TERM_OVERLAP", 1)

    data_dir: Path = Path(_get_env("DATA_DIR", "data"))
    uploads_dir: Path = Path(_get_env("UPLOADS_DIR", "data/uploads"))
    cache_dir: Path = Path(_get_env("CACHE_DIR", "data/cache"))
    logs_dir: Path = Path(_get_env("LOGS_DIR", "data/logs"))
    sqlite_path: Path = Path(_get_env("SQLITE_PATH", "data/cache/metadata.db"))

    api_host: str = _get_env("API_HOST", "127.0.0.1")
    api_port: int = _get_env_int("API_PORT", 8000)
    api_cors_origins: str = _get_env("API_CORS_ORIGINS", "http://localhost:8501")
    api_base_url: str = _get_env("API_BASE_URL", "http://127.0.0.1:8000")
    page_html_max_chars: int = _get_env_int("PAGE_HTML_MAX_CHARS", 1500000)


SETTINGS = Settings()
