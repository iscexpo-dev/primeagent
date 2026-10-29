# wfx-datastax

DataStax component(s) as a standalone Primeagent Extension Bundle.

## Install

```bash
pip install wfx-datastax
```

The bundle is registered automatically via the `primeagent.extensions`
entry-point.  After install, restart your Primeagent server; the bundle's
components will appear in the palette under the `datastax` group with
the namespaced IDs `ext:datastax:<Class>@official`.

## Develop

```bash
cd src/bundles/datastax
pip install -e .
wfx extension validate src/wfx_datastax
```

## Migration

Saved flows referencing the legacy class name(s) or the old import paths
under `wfx.components.datastax.*` are rewritten to the new namespaced
IDs by the migration table in
`src/wfx/src/wfx/extension/migration/migration_table.json`.
