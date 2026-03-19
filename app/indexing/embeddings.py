"""Ollama embedding client wrapper."""

from __future__ import annotations

import requests


class OllamaEmbeddingClient:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            vectors.append(payload.get("embedding", []))
        return vectors

    def embed_query(self, query: str) -> list[float]:
        return self.embed_texts([query])[0]
