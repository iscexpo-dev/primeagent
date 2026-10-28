"""wfx-ibm: IBM bundle (Db2 Vector Store, watsonx.ai LLM and embeddings, watsonx.data Presto and MCP).

This package is the distribution unit ``wfx-ibm``.  At runtime
Primeagent's loader discovers ``extension.json`` shipped alongside this
``__init__.py`` and registers the IBM components under the
namespaced IDs:

* ``ext:ibm:DB2VectorStoreComponent@official``
* ``ext:ibm:WatsonxAIComponent@official``
* ``ext:ibm:WatsonxDataMCPComponent@official``
* ``ext:ibm:WatsonxDataPrestoComponent@official``
* ``ext:ibm:WatsonxEmbeddingsComponent@official``

Third pilot port (after wfx-duckduckgo and wfx-arxiv) -- exercises the
same extraction recipe documented in ``src/bundles/PORTING.md`` against
a multi-component bundle that ships a langchain-community-backed vector
store, the IBM Db2 vendor SDK, and the langchain-ibm watsonx.ai client.
"""

from wfx_ibm.components.ibm.db2_vector import DB2VectorStoreComponent
from wfx_ibm.components.ibm.watsonx import WatsonxAIComponent
from wfx_ibm.components.ibm.watsonx_data_mcp import WatsonxDataMCPComponent
from wfx_ibm.components.ibm.watsonx_data_presto import WatsonxDataPrestoComponent
from wfx_ibm.components.ibm.watsonx_embeddings import WatsonxEmbeddingsComponent

__all__ = [
    "DB2VectorStoreComponent",
    "WatsonxAIComponent",
    "WatsonxDataMCPComponent",
    "WatsonxDataPrestoComponent",
    "WatsonxEmbeddingsComponent",
]
