# wfx-bundles-shim
"""Compatibility shim: wfx.components.azure moved to wfx-azure.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_azure.components.azure")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_azure" or exc.name.startswith("wfx_azure.")):
        msg = (
            "The 'azure' components moved to the 'wfx-azure' distribution. "
            "Install it with: pip install wfx-azure (or pip install primeagent, which includes it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_azure") from exc
    raise
