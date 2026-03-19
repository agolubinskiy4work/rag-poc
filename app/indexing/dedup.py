"""Document deduplication helpers based on content hash."""

from __future__ import annotations


def should_skip_indexing(existing_hash: str | None, new_hash: str) -> bool:
    return bool(existing_hash and existing_hash == new_hash)
