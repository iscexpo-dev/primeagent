"""Compatibility shim for Policies helpers moved to ``wfx-toolguard``."""

from __future__ import annotations

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_toolguard.components.models_and_agents.policies")
except ModuleNotFoundError as exc:
    if exc.name is not None and exc.name.partition(".")[0] != "wfx_toolguard":
        raise
    msg = (
        "The Policies helpers moved to the 'wfx-toolguard' distribution. "
        'Install them with `pip install "wfx[toolguard]"`.'
    )
    raise ModuleNotFoundError(msg) from exc
