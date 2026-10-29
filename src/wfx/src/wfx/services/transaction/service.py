"""Transaction service implementations for wfx."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wfx.services.interfaces import TransactionServiceProtocol

if TYPE_CHECKING:
    from uuid import UUID


class NoopTransactionService(TransactionServiceProtocol):
    """No-operation transaction service for standalone wfx mode.

    This service is used when wfx runs without a concrete transaction
    service implementation (e.g., without primeagent). All operations
    are no-ops and transaction logging is disabled.
    """

    async def log_transaction(
        self,
        flow_id: str,
        vertex_id: str,
        inputs: dict[str, Any] | None,
        outputs: dict[str, Any] | None,
        status: str,
        target_id: str | None = None,
        error: str | None = None,
        *,
        user_id: UUID | None = None,
        session_id: str | None = None,
    ) -> None:
        """No-op implementation of transaction logging.

        In standalone mode, transactions are not persisted.
        """

    def is_enabled(self) -> bool:
        """Transaction logging is disabled in noop mode."""
        return False
