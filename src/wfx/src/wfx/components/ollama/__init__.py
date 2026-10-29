# wfx-bundles-shim
"""Compatibility shim: wfx.components.ollama moved to wfx-ollama.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_ollama.components.ollama")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_ollama" or exc.name.startswith("wfx_ollama.")):
        msg = (
            "The 'ollama' components moved to the 'wfx-ollama' distribution. "
            "Install it with: pip install wfx-ollama (or pip install primeagent, which includes it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_ollama") from exc
    raise
