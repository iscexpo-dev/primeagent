# wfx-azure

Azure OpenAI components and Azure AI Foundry runtime support as a standalone
Primeagent Extension Bundle.

## Install

```bash
pip install wfx-azure
```

`pip install primeagent` includes this bundle because Azure AI Foundry is a
supported model provider. The bundle is registered automatically through the
`primeagent.extensions` entry point and appears under the `azure` group with
canonical component IDs such as
`ext:azure:AzureChatOpenAIComponent@official`.

## Develop

```bash
uv sync
uv run pytest src/bundles/azure/tests -q
uv run wfx extension validate src/bundles/azure/src/wfx_azure
```

The bundle graduated from the manifest-less `wfx-bundles[azure]` provider in
Primeagent 1.12. Its bundle and class names are unchanged, so existing saved
flows retain their canonical IDs.
