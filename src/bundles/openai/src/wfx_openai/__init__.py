"""wfx-openai: OpenAI bundle.

Distribution unit ``wfx-openai``.  At runtime Primeagent's loader
discovers ``extension.json`` shipped alongside this ``__init__.py`` and
registers the bundle's components under the namespaced IDs
``ext:openai:<Class>@official``.
"""

from wfx_openai.components.openai.openai import OpenAIEmbeddingsComponent
from wfx_openai.components.openai.openai_chat_model import OpenAIModelComponent

__all__ = [
    "OpenAIEmbeddingsComponent",
    "OpenAIModelComponent",
]
