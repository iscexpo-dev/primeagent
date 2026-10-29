"""Factory for the durable JobScopedCheckpointStore (LE-1441)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from primeagent.services.checkpoint.store import JobScopedCheckpointStore
from primeagent.services.factory import ServiceFactory

if TYPE_CHECKING:
    from wfx.services.settings.service import SettingsService


class CheckpointServiceFactory(ServiceFactory):
    def __init__(self) -> None:
        super().__init__(JobScopedCheckpointStore)

    @override
    def create(self, settings_service: SettingsService):
        from primeagent.services.jobs.service import JobService

        return JobScopedCheckpointStore(JobService())
