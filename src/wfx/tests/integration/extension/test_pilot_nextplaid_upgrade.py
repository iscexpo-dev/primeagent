"""Integration test: legacy NextPlaid flows upgrade cleanly.

Mirror of ``test_pilot_arxiv_upgrade.py`` for the ``wfx-nextplaid`` bundle,
which ships two components extracted from the pre-bundle in-tree paths:

    * ``NextPlaidVectorStoreComponent`` (was ``wfx.components.nextplaid``)
    * ``VllmMultivectorEmbeddingsComponent`` (was ``wfx.components.vllm``)

Verifies the save/upgrade/load contract for flows referencing either
component by its legacy bare class name or legacy import path, plus the
manifest-shipping contract the loader reads at startup.
"""

from __future__ import annotations

import json
from importlib import metadata as importlib_metadata
from pathlib import Path

import pytest
from wfx.extension.migration.loader import load_migration_table

REPO_ROOT = Path(__file__).resolve().parents[5]
TABLE_PATH = REPO_ROOT / "src" / "wfx" / "src" / "wfx" / "extension" / "migration" / "migration_table.json"

NEXTPLAID_TARGET = "ext:nextplaid:NextPlaidVectorStoreComponent@official"
EMBEDDINGS_TARGET = "ext:nextplaid:VllmMultivectorEmbeddingsComponent@official"


@pytest.fixture(scope="module")
def migration_table():
    table, error = load_migration_table(TABLE_PATH)
    assert error is None, f"failed to load migration table: {error}"
    assert table is not None
    return table


def _saved_flow_node(node_id: str, type_value: str) -> dict:
    """Build a minimal saved-flow node skeleton for testing."""
    return {
        "id": node_id,
        "type": "genericNode",
        "data": {
            "id": node_id,
            "type": type_value,
            "node": {"template": {}},
        },
    }


def _saved_flow(*nodes: dict) -> dict:
    """Wrap nodes in the canonical Primeagent flow envelope."""
    return {"data": {"nodes": list(nodes), "edges": []}}


@pytest.mark.integration
def test_legacy_bare_name_flow_upgrades(migration_table) -> None:
    """Pre-bundle flow saved with the bare class name upgrades to the canonical ID."""
    from wfx.extension.migration.rewrite import migrate_flow_payload

    flow = _saved_flow(_saved_flow_node("nextplaid-1", "NextPlaidVectorStoreComponent"))

    report = migrate_flow_payload(flow, table=migration_table)

    assert report.rewritten_count == 1, "exactly one node should rewrite"
    assert flow["data"]["nodes"][0]["data"]["type"] == NEXTPLAID_TARGET
    [record] = report.records
    assert record.legacy_form_kind == "bare_class_name"
    assert record.new_value == NEXTPLAID_TARGET


@pytest.mark.integration
def test_legacy_import_path_flow_upgrades(migration_table) -> None:
    """A pre-bundle flow saved with the dotted import path upgrades cleanly."""
    from wfx.extension.migration.rewrite import migrate_flow_payload

    flow = _saved_flow(
        _saved_flow_node(
            "nextplaid-2",
            "wfx.components.nextplaid.nextplaid.NextPlaidVectorStoreComponent",
        )
    )

    report = migrate_flow_payload(flow, table=migration_table)
    assert report.rewritten_count == 1
    assert flow["data"]["nodes"][0]["data"]["type"] == NEXTPLAID_TARGET
    assert report.records[0].legacy_form_kind == "import_path"


@pytest.mark.integration
def test_short_import_path_flow_upgrades(migration_table) -> None:
    """Package-level import-path form (re-exported by ``__init__.py``) also upgrades."""
    from wfx.extension.migration.rewrite import migrate_flow_payload

    flow = _saved_flow(_saved_flow_node("nextplaid-3", "wfx.components.nextplaid.NextPlaidVectorStoreComponent"))

    report = migrate_flow_payload(flow, table=migration_table)
    assert report.rewritten_count == 1
    assert flow["data"]["nodes"][0]["data"]["type"] == NEXTPLAID_TARGET


@pytest.mark.integration
def test_legacy_vllm_multivector_embeddings_upgrades(migration_table) -> None:
    """The companion embeddings component, moved out of the core ``vllm`` package, upgrades."""
    from wfx.extension.migration.rewrite import migrate_flow_payload

    flow = _saved_flow(
        _saved_flow_node("npe-1", "VllmMultivectorEmbeddingsComponent"),
        _saved_flow_node(
            "npe-2",
            "wfx.components.vllm.vllm_multivector_embeddings.VllmMultivectorEmbeddingsComponent",
        ),
    )

    report = migrate_flow_payload(flow, table=migration_table)
    assert report.rewritten_count == 2
    assert flow["data"]["nodes"][0]["data"]["type"] == EMBEDDINGS_TARGET
    assert flow["data"]["nodes"][1]["data"]["type"] == EMBEDDINGS_TARGET


@pytest.mark.integration
def test_wfx_nextplaid_distribution_is_importable() -> None:
    """The bundle's package is importable in the development workspace.

    Skipped when the bundle is not installed in the test environment
    (wfx's own venv does not list wfx-nextplaid as a dep); the primeagent
    workspace venv pulls it in transitively from primeagent's pyproject.
    """
    try:
        importlib_metadata.distribution("wfx-nextplaid")
    except importlib_metadata.PackageNotFoundError:
        pytest.skip("wfx-nextplaid not installed in this test environment")

    # Package is present: let a genuine import failure surface rather than skip.
    from wfx_nextplaid import NextPlaidVectorStoreComponent, VllmMultivectorEmbeddingsComponent

    assert NextPlaidVectorStoreComponent.__name__ == "NextPlaidVectorStoreComponent"
    assert VllmMultivectorEmbeddingsComponent.__name__ == "VllmMultivectorEmbeddingsComponent"


def _is_editable_install(dist: importlib_metadata.Distribution) -> bool:
    """Detect an editable install (``pip install -e``)."""
    direct_url = dist.read_text("direct_url.json")
    if not direct_url:
        return False
    try:
        payload = json.loads(direct_url)
    except json.JSONDecodeError:
        return False
    return bool(payload.get("dir_info", {}).get("editable"))


@pytest.mark.integration
def test_wfx_nextplaid_ships_manifest() -> None:
    """``importlib.metadata`` can find ``extension.json`` for the installed dist."""
    try:
        dist = importlib_metadata.distribution("wfx-nextplaid")
    except importlib_metadata.PackageNotFoundError:
        pytest.skip("wfx-nextplaid not installed in this test environment")

    if _is_editable_install(dist):
        import wfx_nextplaid

        package_dir = Path(wfx_nextplaid.__file__).parent
        manifest_path = package_dir / "extension.json"
        assert manifest_path.is_file(), (
            f"wfx-nextplaid source tree at {package_dir} does not ship "
            "extension.json next to __init__.py; the wheel build will not "
            "include it either.  Check pyproject's "
            "[tool.hatch.build.targets.wheel] include rules."
        )
    else:
        files = dist.files or []
        manifests = [f for f in files if f.parts and f.parts[-1] == "extension.json"]
        assert manifests, (
            "wfx-nextplaid distribution does not ship extension.json in its "
            "wheel; the loader will skip it.  Check pyproject's "
            "[tool.hatch.build.targets.wheel] include rules."
        )
        manifest_path = Path(dist.locate_file(manifests[0]))

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["id"] == "wfx-nextplaid"
    assert manifest["wfx"]["compat"] == ["1"]
    assert any(b["name"] == "nextplaid" for b in manifest["bundles"])
