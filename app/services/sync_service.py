"""Service-layer wrapper around indexing sync orchestration."""

from __future__ import annotations

from app.indexing.sync_service import SyncService as IndexSyncService
from app.shared.schemas import SourceInput, SyncResult


class SyncService:
    """Expose sync use-cases for API/UI clients."""

    def __init__(self) -> None:
        self._sync_service = IndexSyncService()

    def run_sync(self, sources: list[SourceInput]) -> SyncResult:
        return self._sync_service.run_sync(sources)
