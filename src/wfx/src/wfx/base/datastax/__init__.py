# wfx-bundles-shim
"""Compatibility shim: wfx.base.datastax moved to the wfx-datastax bundle.

This module re-points to ``wfx_datastax.base`` in the installed bundle
distribution. It exists because component code stored inside saved flows
(and the starter-project templates) imports
``wfx.base.datastax.astradb_base`` directly, and that stored source is
re-executed verbatim at flow build time -- so the legacy path must keep
resolving. It contains no implementations and no third-party
dependencies, and is removed once the deprecation window closes (M4).
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_datastax.base")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_datastax" or exc.name.startswith("wfx_datastax.")):
        msg = (
            "The 'datastax' base utilities moved to the 'wfx-datastax' distribution. "
            "Install it with:  pip install wfx-datastax   "
            "(or 'pip install primeagent', which bundles it)."
        )
        raise ModuleNotFoundError(msg, name="wfx_datastax") from exc
    raise
