"""wfx-oracle: Oracle Database bundle.

Distribution unit ``wfx-oracle``.  At runtime Primeagent's loader
discovers ``extension.json`` shipped alongside this ``__init__.py`` and
registers the bundle's components under the namespaced IDs
``ext:oracle:<Class>@official``.
"""

from wfx_oracle.components.oracle.oracledb_embeddings import OracleEmbeddingsComponent
from wfx_oracle.components.oracle.oracledb_loaders import (
    OracleAutonomousDatabaseLoaderComponent,
    OracleDocLoaderComponent,
)
from wfx_oracle.components.oracle.oraclevs import OracleVectorStoreComponent

__all__ = [
    "OracleAutonomousDatabaseLoaderComponent",
    "OracleDocLoaderComponent",
    "OracleEmbeddingsComponent",
    "OracleVectorStoreComponent",
]
