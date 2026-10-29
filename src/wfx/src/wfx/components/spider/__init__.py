# wfx-bundles-shim
"""Compatibility shim: wfx.components.spider re-points to wfx-bundles.

The SpiderTool component lives in the ``wfx-bundles`` distribution; this module
aliases the old in-tree import path to it and ships no implementation and no
third-party dependency.  It exists so legacy ``wfx.components.spider`` imports
resolve and the i18n string extractor (which walks ``wfx.components``) keeps
emitting SpiderTool's translation keys.  Removed at the M4 shim cleanup.
"""

import importlib
import sys

try:
    sys.modules[__name__] = importlib.import_module("wfx_bundles.spider")
except ModuleNotFoundError as exc:
    if exc.name is not None and (exc.name == "wfx_bundles" or exc.name.startswith("wfx_bundles.")):
        msg = (
            "The 'spider' components moved to the 'wfx-bundles' distribution. Install it with: pip install wfx-bundles."
        )
        raise ModuleNotFoundError(msg, name="wfx_bundles") from exc
    raise
