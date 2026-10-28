# wfx-bundles-shim
"""Compatibility shim: wfx.components.openai moved to the wfx-openai bundle.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_openai.components.openai")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_openai" or exc.name.startswith("wfx_openai.")):
        msg = (
            "The 'openai' components moved to the 'wfx-openai' distribution. "
            "Install it with:  pip install wfx-openai   "
            "(or 'pip install primeagent', which bundles it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_openai") from exc
    raise
