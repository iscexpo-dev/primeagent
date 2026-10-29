"""wfx-valkey: Valkey bundle.

Distribution unit ``wfx-valkey``.  At runtime Primeagent's loader
discovers ``extension.json`` shipped alongside this ``__init__.py`` and
registers the bundle's components under the namespaced IDs
``ext:valkey:<Class>@official``.
"""

from wfx_valkey.components.valkey.valkey import ValkeyVectorStoreComponent
from wfx_valkey.components.valkey.valkey_chat import ValkeyIndexChatMemory

__all__ = [
    "ValkeyIndexChatMemory",
    "ValkeyVectorStoreComponent",
]
