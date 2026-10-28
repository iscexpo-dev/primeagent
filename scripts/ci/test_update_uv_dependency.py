"""Regression tests for the nightly full -> base dependency rewrite."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import update_uv_dependency as mod


def test_pins_root_base_and_optional_extras(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(
        "[project]\n"
        'dependencies = ["primeagent-base~=1.12.0", "wfx-bundles>=1.1,<2.0"]\n'
        "[project.optional-dependencies]\n"
        'audio = ["primeagent-base[audio]~=1.12.0"]\n'
        'postgresql = ["primeagent-base[postgresql]>=1.12.0,<1.13.dev0"]\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "BASE_DIR", tmp_path)

    mod.update_uv_dep("1.12.0.dev26")

    result = path.read_text(encoding="utf-8")
    assert '"primeagent-base==1.12.0.dev26"' in result
    assert '"primeagent-base[audio]==1.12.0.dev26"' in result
    assert '"primeagent-base[postgresql]==1.12.0.dev26"' in result
    assert '"wfx-bundles>=1.1,<2.0"' in result


def test_raises_without_base_dependency(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\ndependencies = ["wfx~=1.12.0"]\n', encoding="utf-8")
    monkeypatch.setattr(mod, "BASE_DIR", tmp_path)

    with pytest.raises(ValueError, match="UV dependency not found"):
        mod.update_uv_dep("1.12.0.dev26")
