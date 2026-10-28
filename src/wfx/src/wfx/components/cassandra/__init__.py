# wfx-compat-shim
"""Compatibility shim for Cassandra components moved to ``wfx-datastax``."""

from __future__ import annotations

import importlib
import sys

try:
    canonical_package = "wfx_datastax.components.cassandra"
    for module_name in ("cassandra", "cassandra_chat", "cassandra_graph"):
        sys.modules[f"{__name__}.{module_name}"] = importlib.import_module(f"{canonical_package}.{module_name}")
    sys.modules[__name__] = importlib.import_module(canonical_package)
except ModuleNotFoundError as exc:
    if exc.name is not None and exc.name.partition(".")[0] != "wfx_datastax":
        raise
    msg = (
        "The Cassandra components moved to the 'wfx-datastax' distribution. "
        'Install them with `pip install "wfx[cassandra]"`.'
    )
    raise ModuleNotFoundError(msg) from exc
