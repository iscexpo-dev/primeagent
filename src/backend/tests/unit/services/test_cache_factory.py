"""Regression tests for the cache factory after diskcache removal."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from wfx.services.settings.base import Settings


def test_cache_type_disk_is_rejected(monkeypatch):
    """PRIMEAGENT_CACHE_TYPE=disk must fail validation now that the disk backend is gone."""
    monkeypatch.setenv("PRIMEAGENT_CACHE_TYPE", "disk")
    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize("cache_type", ["async", "memory", "redis"])
def test_supported_cache_types_validate(monkeypatch, cache_type):
    monkeypatch.setenv("PRIMEAGENT_CACHE_TYPE", cache_type)
    settings = Settings()
    assert settings.cache_type == cache_type
