"""Shared base infrastructure for the datastax bundle.

Houses the mixin(s) every component in this bundle inherits from --
pre-extraction this lived at ``wfx.base.datastax``.  Moved into the
bundle (not kept in wfx) because it is datastax-specific and only ever
imported by the datastax components.
"""

from wfx_datastax.base.astradb_base import AstraDBBaseComponent

__all__ = [
    "AstraDBBaseComponent",
]
