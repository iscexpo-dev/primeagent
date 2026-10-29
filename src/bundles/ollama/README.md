# wfx-ollama

Ollama language-model and embedding components as a standalone Primeagent
Extension Bundle.

## Install

```bash
pip install wfx-ollama
```

`pip install primeagent` includes this bundle because Ollama is a supported model
provider. The bundle is registered automatically through the
`primeagent.extensions` entry point and appears under the `ollama` group with
canonical component IDs such as `ext:ollama:ChatOllamaComponent@official`.

## Develop

```bash
uv sync
uv run pytest src/bundles/ollama/tests -q
uv run wfx extension validate src/bundles/ollama/src/wfx_ollama
```

The bundle graduated from the manifest-less `wfx-bundles[ollama]` provider in
Primeagent 1.12. Its bundle and class names are unchanged, so existing saved
flows retain their canonical IDs.
