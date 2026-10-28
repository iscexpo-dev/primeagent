"""wfx-amazon: Amazon bundle.

Distribution unit ``wfx-amazon``.  At runtime Primeagent's loader
discovers ``extension.json`` shipped alongside this ``__init__.py`` and
registers the bundle's components under the namespaced IDs
``ext:amazon:<Class>@official``.
"""

from wfx_amazon.components.amazon.amazon_bedrock_converse import AmazonBedrockConverseComponent
from wfx_amazon.components.amazon.amazon_bedrock_embedding import AmazonBedrockEmbeddingsComponent
from wfx_amazon.components.amazon.amazon_bedrock_model import AmazonBedrockComponent
from wfx_amazon.components.amazon.s3_bucket_uploader import S3BucketUploaderComponent

__all__ = [
    "AmazonBedrockComponent",
    "AmazonBedrockConverseComponent",
    "AmazonBedrockEmbeddingsComponent",
    "S3BucketUploaderComponent",
]
