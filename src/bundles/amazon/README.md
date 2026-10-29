# wfx-amazon

Amazon component(s) as a standalone Primeagent Extension Bundle.

## Install

```bash
pip install wfx-amazon
```

The bundle is registered automatically via the `primeagent.extensions`
entry-point.  After install, restart your Primeagent server; the bundle's
components will appear in the palette under the `amazon` group with
the namespaced IDs `ext:amazon:<Class>@official`.

## Develop

```bash
cd src/bundles/amazon
pip install -e .
wfx extension validate src/wfx_amazon
```

## Migration

Saved flows referencing the legacy class name(s) or the old import paths
under `wfx.components.amazon.*` are rewritten to the new namespaced
IDs by the migration table in
`src/wfx/src/wfx/extension/migration/migration_table.json`.
