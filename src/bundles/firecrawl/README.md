# wfx-firecrawl

Firecrawl components (Scrape, Crawl, Map, and Search APIs) as a standalone
Primeagent Extension Bundle, built against the firecrawl-py v2 SDK.

## Install

```bash
pip install wfx-firecrawl
```

The bundle is registered automatically via the `primeagent.extensions`
entry-point.  After install, restart your Primeagent server; the bundle's
components will appear in the palette under the `firecrawl` group.

## Develop

```bash
cd src/bundles/firecrawl
pip install -e .
wfx extension validate src/wfx_firecrawl
```

## Migration

Saved flows referencing the legacy class name(s) or the old import paths
under `wfx.components.firecrawl.*` are rewritten to the new namespaced
IDs by the migration table in
`src/wfx/src/wfx/extension/migration/migration_table.json`.
