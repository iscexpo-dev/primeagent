"""Exceptions raised by the Primeagent SDK."""

from __future__ import annotations


class PrimeagentError(Exception):
    """Base class for all Primeagent SDK errors."""


class PrimeagentHTTPError(PrimeagentError):
    """An HTTP error was returned by the Primeagent API."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class PrimeagentNotFoundError(PrimeagentHTTPError):
    """The requested resource was not found (404)."""


class PrimeagentAuthError(PrimeagentHTTPError):
    """Authentication failed (401/403)."""


class PrimeagentValidationError(PrimeagentHTTPError):
    """The request payload was rejected by the server (422)."""


class PrimeagentConnectionError(PrimeagentError):
    """Could not connect to the Primeagent instance."""


class PrimeagentTimeoutError(PrimeagentError):
    """A background job or polling operation exceeded its timeout.

    Adapted from ``PrimeagentV2TimeoutError`` in khulnasoft-bot/sdk PR #1
    (Janardan Singh Kavia, IBM Corp., Apache 2.0).
    """


class EnvironmentNotFoundError(PrimeagentError):
    """The named environment is not defined in the environments config."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(
            f"Environment {name!r} not found. Check your primeagent-environments.toml (or PRIMEAGENT_ENV variable)."
        )


class EnvironmentConfigError(PrimeagentError):
    """The environments config file is malformed or missing required fields."""
