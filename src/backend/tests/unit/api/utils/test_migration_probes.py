"""Credential-free migration locations preserve the distinction between IPv6 hosts and ports."""

import pytest
from primeagent.api.utils.migration_probes import location


@pytest.mark.parametrize(
    ("address", "expected"),
    [
        ("postgresql://db.internal/primeagent", "db.internal/primeagent"),
        ("postgresql://db.internal:5432/primeagent", "db.internal:5432/primeagent"),
        ("postgresql://[::1]/primeagent", "[::1]/primeagent"),
        ("postgresql://[::1]:5432/primeagent", "[::1]:5432/primeagent"),
    ],
)
def test_locations_keep_hosts_and_ports_unambiguous(address, expected):
    assert location(address) == expected
