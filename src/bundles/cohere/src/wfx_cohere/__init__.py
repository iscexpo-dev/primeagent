"""wfx-cohere: Cohere bundle.

Distribution unit ``wfx-cohere``.  At runtime Primeagent's loader
discovers ``extension.json`` shipped alongside this ``__init__.py`` and
registers the bundle's components under the namespaced IDs
``ext:cohere:<Class>@official``.
"""

from wfx_cohere.components.cohere.cohere_embeddings import CohereEmbeddingsComponent
from wfx_cohere.components.cohere.cohere_models import CohereComponent
from wfx_cohere.components.cohere.cohere_rerank import CohereRerankComponent

__all__ = [
    "CohereComponent",
    "CohereEmbeddingsComponent",
    "CohereRerankComponent",
]
