# wfx-bundles-shim
"""Compatibility shim: wfx.components.datastax moved to the wfx-datastax bundle.

This module re-points to the installed bundle distribution. It contains
no component implementations and no third-party dependencies, and is
removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_datastax.components.datastax")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_datastax" or exc.name.startswith("wfx_datastax.")):
        msg = (
            "The 'datastax' components moved to the 'wfx-datastax' distribution. "
            "Install it with:  pip install wfx-datastax   "
            "(or 'pip install primeagent', which bundles it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_datastax") from exc
    raise
