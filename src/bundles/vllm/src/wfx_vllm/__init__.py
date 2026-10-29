"""wfx-vllm: vLLM model-provider bundle.

Distribution unit ``wfx-vllm``. At runtime Primeagent's loader discovers the
``extension.json`` shipped alongside this ``__init__.py`` and registers its
``providers[]`` entry, merging a **vLLM** provider into the unified model
system. vLLM is OpenAI-compatible, so the provider reuses ``ChatOpenAI`` /
``OpenAIEmbeddings`` and discovers models live from the server's ``/v1/models``
endpoint (see :mod:`wfx_vllm.discovery`).

Inherits the original vLLM provider contributed in
https://github.com/khulnasoft-bot/primeagent/pull/13910 by Yash Pareek.
"""
