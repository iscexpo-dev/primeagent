"""Telemetry service package.

Stable enterprise extension points are re-exported here so that enterprise
consumers have an import path that survives internal module restructuring::

    from primeagent.services.telemetry import pop_all, append_run_event
"""

from primeagent.services.telemetry.run_event_store import append_run_event, pop_all

__all__ = ["append_run_event", "pop_all"]
