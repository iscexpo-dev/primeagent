"""wfx-serply: Serply Search bundle.

This package is the distribution unit ``wfx-serply``.  At runtime
Primeagent's loader discovers ``extension.json`` shipped alongside this
``__init__.py`` and registers ``SerplySearchComponent`` under the
namespaced ID ``ext:serply:SerplySearchComponent@official``.

Serply (https://serply.io) is a SERP API; the component calls its
search endpoint directly with ``httpx`` and needs only a user-supplied
API key, so the bundle carries no vendor SDK dependency.
"""

from wfx_serply.components.serply.serply_search import SerplySearchComponent

__all__ = ["SerplySearchComponent"]
