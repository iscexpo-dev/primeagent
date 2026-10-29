"""wfx-anthropic: Anthropic bundle.

Distribution unit ``wfx-anthropic``.  At runtime Primeagent's loader
discovers ``extension.json`` shipped alongside this ``__init__.py`` and
registers the bundle's components under the namespaced IDs
``ext:anthropic:<Class>@official``.
"""

from wfx_anthropic.components.anthropic.anthropic import AnthropicModelComponent

__all__ = [
    "AnthropicModelComponent",
]
