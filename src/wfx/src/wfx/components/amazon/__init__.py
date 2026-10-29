# wfx-bundles-shim
"""Compatibility shim: wfx.components.amazon moved to the wfx-amazon bundle.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_amazon.components.amazon")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_amazon" or exc.name.startswith("wfx_amazon.")):
        msg = (
            "The 'amazon' components moved to the 'wfx-amazon' distribution. "
            "Install it with:  pip install wfx-amazon   "
            "(or 'pip install primeagent', which bundles it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_amazon") from exc
    raise
