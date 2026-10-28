# wfx-openai

OpenAI component(s) as a standalone Primeagent Extension Bundle.

## Install

```bash
pip install wfx-openai
```

The bundle is registered automatically via the `primeagent.extensions`
entry-point.  After install, restart your Primeagent server; the bundle's
components will appear in the palette under the `openai` group with
the namespaced IDs `ext:openai:<Class>@official`.

## Develop

```bash
cd src/bundles/openai
pip install -e .
wfx extension validate src/wfx_openai
```

## Migration

Saved flows referencing the legacy class name(s) or the old import paths
under `wfx.components.openai.*` are rewritten to the new namespaced
IDs by the migration table in
`src/wfx/src/wfx/extension/migration/migration_table.json`.
