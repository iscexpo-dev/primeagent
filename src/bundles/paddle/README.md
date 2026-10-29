# wfx-paddle

PaddleOCR as a standalone Primeagent Extension Bundle.

Ships the **PaddleOCR** component, which performs either layout-aware document
parsing into Markdown (`PP-StructureV3`, `PaddleOCR-VL-1.6`) or plain OCR text
recognition (`PP-OCRv5`, `PP-OCRv6`). It talks to the PaddleOCR
[AI Studio async Job HTTP API](https://paddlepaddle.github.io/PaddleOCR/latest/en/version3.x/paddleocr_and_ppstructure.html)
(`submit -> poll -> fetch`) directly via `httpx`, so it does **not** require the
`paddleocr` Python SDK (whose transitive `pyyaml` constraint conflicts with
Primeagent's dependency tree).

## Install

```bash
pip install wfx-paddle
```

The bundle is registered automatically via the `primeagent.extensions`
entry-point. After install, restart your Primeagent server; the component will
appear in the palette under the `paddle` group.

You will need an AI Studio access token
(<https://aistudio.baidu.com/account/accessToken>) to run the component.

## Develop

```bash
cd src/bundles/paddle
pip install -e .
wfx extension validate src/wfx_paddle
```

## Migration

Saved flows referencing the legacy class name or the old import paths under
`wfx.components.paddle.*` are rewritten to the new namespaced ID
`ext:paddle:PaddleOCRComponent@official` by the migration table in
`src/wfx/src/wfx/extension/migration/migration_table.json`.
