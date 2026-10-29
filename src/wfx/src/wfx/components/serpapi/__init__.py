# wfx-bundles-shim
"""Compatibility shim: wfx.components.serpapi moved to wfx-bundles.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_bundles.serpapi")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_bundles" or exc.name.startswith("wfx_bundles.")):
        msg = (
            "The 'serpapi' components moved to the 'wfx-bundles' distribution. "
            "Install it with: pip install wfx-bundles."
        )
        raise ModuleNotFoundError(msg, name="wfx_bundles") from exc
    raise
