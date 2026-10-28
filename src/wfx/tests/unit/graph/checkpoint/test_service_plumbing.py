"""CHECKPOINT_SERVICE plumbing + wfx-standalone boundary (LE-1440)."""

from __future__ import annotations

import re
from pathlib import Path

import wfx.graph.checkpoint.builder
import wfx.graph.checkpoint.probe
import wfx.graph.checkpoint.resume
import wfx.graph.checkpoint.schema
import wfx.graph.checkpoint.store
import wfx.graph.exceptions
from wfx.graph.checkpoint.store import InMemoryCheckpointStore
from wfx.services.deps import get_checkpoint_service
from wfx.services.schema import ServiceType

_CHECKPOINT_MODULES = (
    wfx.graph.checkpoint.schema,
    wfx.graph.checkpoint.store,
    wfx.graph.checkpoint.builder,
    wfx.graph.checkpoint.resume,
    wfx.graph.checkpoint.probe,
    wfx.graph.exceptions,
)


def test_checkpoint_service_type_registered():
    assert ServiceType.CHECKPOINT_SERVICE == "checkpoint_service"


def test_get_checkpoint_service_falls_back_to_in_memory_singleton():
    first = get_checkpoint_service()
    second = get_checkpoint_service()
    assert isinstance(first, InMemoryCheckpointStore)
    assert first is second


def test_checkpoint_modules_never_import_primeagent():
    pattern = re.compile(r"^\s*(from|import)\s+primeagent", re.MULTILINE)
    for module in _CHECKPOINT_MODULES:
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert not pattern.search(source), f"{module.__name__} imports primeagent — wfx must stay standalone"
