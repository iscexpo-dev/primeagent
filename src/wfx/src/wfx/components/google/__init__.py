# wfx-bundles-shim
"""Compatibility shim: wfx.components.google moved to wfx-google.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_google.components.google")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_google" or exc.name.startswith("wfx_google.")):
        msg = (
            "The 'google' components moved to the 'wfx-google' distribution. "
            "Install it with: pip install wfx-google (or pip install primeagent, which includes it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_google") from exc
    raise
