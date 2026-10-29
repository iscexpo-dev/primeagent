"""Regression tests for full-package requirements on newly introduced bundle RCs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import tomllib
from packaging.requirements import Requirement
from packaging.version import Version

sys.path.insert(0, str(Path(__file__).resolve().parent))

from update_bundle_prerelease_dependencies import update_bundle_prerelease_dependencies


def _write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "primeagent"
version = "1.11.0rc2"
dependencies = [
    "primeagent-base>=1.12.0rc2,<1.13.dev0",
    "wfx-new-provider>=0.1.0,<1.0.0",
    "wfx-bundles[all-no-torch]>=1.1,<2.0",
    "wfx-final-provider>=0.1.0,<1.0.0",
]
[project.optional-dependencies]
new-provider = ["wfx-new-provider[documents]>=0.1.0,<1.0.0"]
""",
        encoding="utf-8",
    )
    manifest = tmp_path / "bundle-version-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "wfx-new-provider": "0.1.0rc2",
                "wfx-bundles": "1.1.0rc2",
                "wfx-final-provider": "0.1.0",
            }
        ),
        encoding="utf-8",
    )
    return pyproject, manifest


def test_new_bundle_rcs_satisfy_rewritten_main_requirements(tmp_path: Path) -> None:
    pyproject, manifest = _write_inputs(tmp_path)

    assert update_bundle_prerelease_dependencies(pyproject, manifest) == 3

    project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
    requirements = {Requirement(value).name: Requirement(value) for value in project["dependencies"]}
    optional_requirement = Requirement(project["optional-dependencies"]["new-provider"][0])
    assert requirements["wfx-new-provider"].specifier.contains(Version("0.1.0rc2"))
    assert requirements["wfx-bundles"].specifier.contains(Version("1.1.0rc2"))
    assert requirements["wfx-bundles"].extras == {"all-no-torch"}
    assert "<2.0" in str(requirements["wfx-bundles"].specifier)
    assert str(requirements["wfx-final-provider"].specifier) == "<1.0.0,>=0.1.0"
    assert optional_requirement.specifier.contains(Version("0.1.0rc2"))
    assert optional_requirement.extras == {"documents"}


def test_unsupported_prerelease_requirement_fails_closed(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "primeagent"\nversion = "1.11.0rc2"\ndependencies = ["wfx-new-provider~=0.1.0"]\n',
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"wfx-new-provider": "0.1.0rc2"}', encoding="utf-8")

    with pytest.raises(ValueError, match="Cannot rewrite the lower bound"):
        update_bundle_prerelease_dependencies(pyproject, manifest)


def test_all_final_bundle_manifest_is_a_noop(tmp_path: Path) -> None:
    pyproject, manifest = _write_inputs(tmp_path)
    manifest.write_text(
        '{"wfx-new-provider": "0.1.0", "wfx-bundles": "1.1.0", "wfx-final-provider": "0.1.0"}',
        encoding="utf-8",
    )
    before = pyproject.read_text(encoding="utf-8")

    assert update_bundle_prerelease_dependencies(pyproject, manifest) == 0
    assert pyproject.read_text(encoding="utf-8") == before
