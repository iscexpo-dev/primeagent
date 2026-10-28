# wfx-oracle

Oracle Database components (Doc Loader, Autonomous Database Loader,
Embeddings, Vector Store) as a standalone Primeagent Extension Bundle.

## Install

```bash
pip install wfx-oracle
```

The bundle is registered automatically via the `primeagent.extensions`
entry-point.  After install, restart your Primeagent server; the bundle's
components will appear in the palette under the `Oracle` group.

## Develop

```bash
cd src/bundles/oracle
pip install -e .
wfx extension validate src/wfx_oracle
```

## Migration

Saved flows referencing the legacy class name(s) or the old import paths
under `wfx.components.oracledb.*` are rewritten to the new namespaced
IDs by the migration table in
`src/wfx/src/wfx/extension/migration/migration_table.json`.
