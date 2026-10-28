"""Tests for ``scripts/ci/sync_bundle_wfx_pin.py``.

The ``make patch`` target calls this script to keep every ``src/bundles/*``
package's ``wfx`` runtime-dependency floor in step with the Primeagent/WFX
``major.minor`` line. These tests exercise the real script module so a
regression in the floor format or the dependency regex is caught without
running ``make``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10: tomllib is stdlib only on 3.11+
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parents[4]
_SCRIPT = REPO_ROOT / "scripts" / "ci" / "sync_bundle_wfx_pin.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("sync_bundle_wfx_pin", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sync_bundle_wfx_pin"] = module
    spec.loader.exec_module(module)
    return module


mod = _load_module()


# ---------------------------------------------------------------------------
# wfx_floor_spec
# ---------------------------------------------------------------------------


class TestWfxFloorSpec:
    # The .dev0 floor is load-bearing: nightlies are canonical X.Y.0.devN
    # pre-releases, which PEP 440 sorts BELOW X.Y.0, so a plain >=X.Y.0
    # floor makes the branch's own nightly wfx unresolvable.
    @pytest.mark.parametrize(
        ("version", "expected"),
        [
            ("1.10.0", "wfx>=1.10.0.dev0,<2.0.0"),
            ("1.10.3", "wfx>=1.10.0.dev0,<2.0.0"),  # patch within a minor -> same floor
            ("1.11.0", "wfx>=1.11.0.dev0,<2.0.0"),
            ("2.0.0", "wfx>=2.0.0.dev0,<3.0.0"),
            ("v1.10.0", "wfx>=1.10.0.dev0,<2.0.0"),  # leading v tolerated
            ("10.4.2", "wfx>=10.4.0.dev0,<11.0.0"),  # multi-digit major
        ],
    )
    def test_floor(self, version, expected):
        assert mod.wfx_floor_spec(version) == expected

    @pytest.mark.parametrize("bad", ["", "1.10", "abc", "1", "x.y.z"])
    def test_rejects_unparseable(self, bad):
        with pytest.raises(ValueError, match="Unparseable version"):
            mod.wfx_floor_spec(bad)


# ---------------------------------------------------------------------------
# rewrite_wfx_dep
# ---------------------------------------------------------------------------


class TestRewriteWfxDep:
    FLOOR = "wfx>=1.10.0.dev0,<2.0.0"

    def test_rewrites_bare_floor(self):
        assert mod.rewrite_wfx_dep('    "wfx>=0.5.0",', self.FLOOR) == f'    "{self.FLOOR}",'

    def test_rewrites_existing_range(self):
        assert mod.rewrite_wfx_dep('    "wfx>=1.9.0,<2.0.0",', self.FLOOR) == f'    "{self.FLOOR}",'

    def test_rewrites_compatible_release_and_equality(self):
        assert mod.rewrite_wfx_dep('"wfx~=0.5.0"', self.FLOOR) == f'"{self.FLOOR}"'
        assert mod.rewrite_wfx_dep('"wfx==0.5.0"', self.FLOOR) == f'"{self.FLOOR}"'

    def test_idempotent(self):
        once = mod.rewrite_wfx_dep('"wfx>=0.5.0"', self.FLOOR)
        assert mod.rewrite_wfx_dep(once, self.FLOOR) == once

    def test_leaves_self_reference_untouched(self):
        # docling's optional-deps self-ref must NOT be treated as the wfx dep.
        for self_ref in ('"wfx-docling[local]"', '"wfx-docling[local,chunking,image-description]"'):
            assert mod.rewrite_wfx_dep(self_ref, self.FLOOR) == self_ref

    def test_leaves_nightly_form_untouched(self):
        # Legacy form from the retired nightly bundle-rename track (see
        # src/bundles/NIGHTLY.md); sync must not clobber it if encountered.
        assert mod.rewrite_wfx_dep('"wfx-nightly==1.10.0.dev38"', self.FLOOR) == '"wfx-nightly==1.10.0.dev38"'

    def test_only_rewrites_runtime_dep_in_full_block(self):
        content = (
            "dependencies = [\n"
            '    "wfx>=0.5.0",\n'
            '    "langchain-community>=0.4.1,<1.0.0",\n'
            "]\n"
            "[project.optional-dependencies]\n"
            "all = [\n"
            '    "wfx-docling[local,chunking,image-description]",\n'
            "]\n"
        )
        out = mod.rewrite_wfx_dep(content, self.FLOOR)
        assert f'    "{self.FLOOR}",' in out
        assert '    "langchain-community>=0.4.1,<1.0.0",' in out  # untouched
        assert '    "wfx-docling[local,chunking,image-description]",' in out  # untouched


# ---------------------------------------------------------------------------
# sync_bundles (filesystem-level, on a temp tree)
# ---------------------------------------------------------------------------


class TestSyncBundles:
    def _make_bundle(self, bundles_dir: Path, name: str, wfx_line: str) -> Path:
        d = bundles_dir / name
        d.mkdir(parents=True)
        pyproject = d / "pyproject.toml"
        content = f'[project]\nname = "wfx-{name}"\ndependencies = [\n    "{wfx_line}",\n]\n'
        pyproject.write_text(content, encoding="utf-8")
        return pyproject

    def test_sync_updates_and_reports(self, tmp_path):
        bundles = tmp_path / "bundles"
        self._make_bundle(bundles, "arxiv", "wfx>=0.5.0")
        self._make_bundle(bundles, "ibm", "wfx>=1.10.0.dev0,<2.0.0")  # already correct

        results = dict(mod.sync_bundles("1.10.0", bundles))
        assert results == {"arxiv": True, "ibm": False}  # arxiv changed, ibm no-op
        assert '"wfx>=1.10.0.dev0,<2.0.0"' in (bundles / "arxiv" / "pyproject.toml").read_text()

    def test_sync_idempotent(self, tmp_path):
        bundles = tmp_path / "bundles"
        self._make_bundle(bundles, "arxiv", "wfx>=0.5.0")
        mod.sync_bundles("1.10.0", bundles)
        second = dict(mod.sync_bundles("1.10.0", bundles))
        assert second == {"arxiv": False}


def test_bundle_manifests_match_distribution_versions():
    """Keep published extension identity aligned with wheel metadata."""
    for pyproject in sorted((REPO_ROOT / "src" / "bundles").glob("*/pyproject.toml")):
        project_version = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
        manifests = sorted(pyproject.parent.glob("src/*/extension.json"))
        if pyproject.parent.name != "wfx-bundles":
            assert manifests, f"{pyproject.relative_to(REPO_ROOT)} is missing extension.json"
        for manifest in manifests:
            manifest_version = json.loads(manifest.read_text(encoding="utf-8"))["version"]
            assert manifest_version == project_version, (
                f"{manifest.relative_to(REPO_ROOT)} has version {manifest_version}, "
                f"but {pyproject.relative_to(REPO_ROOT)} has {project_version}"
            )


# ---------------------------------------------------------------------------
# ratchet_spec -- sync must never WIDEN an existing pin
# ---------------------------------------------------------------------------


class TestRatchetSpec:
    GEN_1_11 = "wfx>=1.11.0.dev0,<2.0.0"
    GEN_1_12 = "wfx>=1.12.0.dev0,<2.0.0"

    def test_keeps_hand_tightened_maintenance_pin(self):
        # The regression this guards: `make patch v=1.11.7` on release-1.11.x
        # regenerating <2.0.0 would let a 1.11-line bundle satisfy a 1.12
        # install. The 1.11 bundle numbers sort higher, so the resolver would
        # prefer them and primeagent 1.12 would silently get 1.11-line code.
        assert mod.ratchet_spec("wfx>=1.11.6,<1.12", self.GEN_1_11) == "wfx>=1.11.6,<1.12"

    def test_generated_pin_is_a_noop_on_itself(self):
        assert mod.ratchet_spec(self.GEN_1_12, self.GEN_1_12) == self.GEN_1_12

    def test_stale_floor_is_still_raised(self):
        assert mod.ratchet_spec("wfx>=1.9.0,<2.0.0", self.GEN_1_11) == self.GEN_1_11

    def test_line_move_supersedes_rather_than_emptying(self):
        # Intersecting here would yield ">=1.12.0.dev0,<1.12" -- unsatisfiable.
        assert mod.ratchet_spec("wfx>=1.11.6,<1.12", self.GEN_1_12) == self.GEN_1_12

    def test_cap_padding(self):
        # "<1.12" and "<1.12.0" are the same bound, so both are line moves.
        assert mod.ratchet_spec("wfx>=1.11.6,<1.12.0", self.GEN_1_12) == self.GEN_1_12

    @pytest.mark.parametrize("legacy", ["wfx>=0.5.0", "wfx~=0.5.0", "wfx==0.5.0"])
    def test_legacy_forms_normalise_wholesale(self, legacy):
        assert mod.ratchet_spec(legacy, self.GEN_1_11) == self.GEN_1_11


def test_sync_preserves_a_tightened_maintenance_pin(tmp_path):
    """End-to-end: `make patch v=1.11.7` on a 1.11.x-shaped tree is a no-op."""
    bundles = tmp_path / "bundles"
    (bundles / "amazon").mkdir(parents=True)
    pyproject = bundles / "amazon" / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "wfx-amazon"\ndependencies = [\n    "wfx>=1.11.6,<1.12",\n]\n',
        encoding="utf-8",
    )

    assert dict(mod.sync_bundles("1.11.7", bundles)) == {"amazon": False}
    assert '"wfx>=1.11.6,<1.12"' in pyproject.read_text(encoding="utf-8")
