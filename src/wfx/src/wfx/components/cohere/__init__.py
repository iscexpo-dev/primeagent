# wfx-bundles-shim
"""Compatibility shim: wfx.components.cohere moved to the wfx-cohere bundle.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_cohere.components.cohere")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_cohere" or exc.name.startswith("wfx_cohere.")):
        msg = (
            "The 'cohere' components moved to the 'wfx-cohere' distribution. "
            "Install it with:  pip install wfx-cohere   "
            "(or 'pip install primeagent', which bundles it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_cohere") from exc
    raise
