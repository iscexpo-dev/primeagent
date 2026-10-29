# wfx-bundles-shim
"""Import-only compatibility for retired Chroma components, excluded from discovery."""

from wfx.components.chroma.chroma import ChromaVectorStoreComponent
from wfx.components.chroma.local_db import LocalDBComponent

__all__ = ["ChromaVectorStoreComponent", "LocalDBComponent"]
