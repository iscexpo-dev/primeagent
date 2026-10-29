# wfx-anthropic

Anthropic component(s) as a standalone Primeagent Extension Bundle.

## Install

```bash
pip install wfx-anthropic
```

The bundle is registered automatically via the `primeagent.extensions`
entry-point.  After install, restart your Primeagent server; the bundle's
components will appear in the palette under the `anthropic` group with
the namespaced IDs `ext:anthropic:<Class>@official`.

## Develop

```bash
cd src/bundles/anthropic
pip install -e .
wfx extension validate src/wfx_anthropic
```

## Migration

Saved flows referencing the legacy class name(s) or the old import paths
under `wfx.components.anthropic.*` are rewritten to the new namespaced
IDs by the migration table in
`src/wfx/src/wfx/extension/migration/migration_table.json`.
