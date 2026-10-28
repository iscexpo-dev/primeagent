# wfx-bundles-shim
"""Compatibility shim: wfx.components.exa moved to the wfx-exa bundle.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_exa.components.exa")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_exa" or exc.name.startswith("wfx_exa.")):
        msg = (
            "The 'exa' components moved to the 'wfx-exa' distribution. "
            "Install it with:  pip install wfx-exa   "
            "(or 'pip install primeagent', which bundles it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_exa") from exc
    raise
