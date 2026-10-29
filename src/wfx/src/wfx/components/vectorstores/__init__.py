# wfx-bundles-shim
"""Historical Local DB imports remain available without optional provider SDKs."""

from wfx.components.chroma.local_db import LocalDBComponent

__all__ = ["LocalDBComponent"]
