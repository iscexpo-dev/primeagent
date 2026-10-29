# wfx-bundles-shim
"""Compatibility shim: wfx.components.anthropic moved to the wfx-anthropic bundle.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_anthropic.components.anthropic")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_anthropic" or exc.name.startswith("wfx_anthropic.")):
        msg = (
            "The 'anthropic' components moved to the 'wfx-anthropic' distribution. "
            "Install it with:  pip install wfx-anthropic   "
            "(or 'pip install primeagent', which bundles it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_anthropic") from exc
    raise
