"""Content cleaning for parsed documents."""

from __future__ import annotations

import re

from app.shared.utils import normalize_text


def clean_text(text: str) -> str:
    cleaned = text
    cleaned = re.sub(r"\b(cookie|privacy policy|terms of use)\b", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned)
    cleaned = normalize_text(cleaned)
    return cleaned
