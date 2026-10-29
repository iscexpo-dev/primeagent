"""Regression tests for ``update_lf_base_dependency``.

The nightly bump pins base's ``wfx`` dependency to the exact ``==X.Y.0.devN`` so the dev
release resolves down the tree. Base also carries compatibility ``wfx[extra]`` references
for the relocated Cassandra and ToolGuard features. If those keep a
``~=X.Y.0`` floor while the bare ``wfx`` dep is pinned to the dev version, the floor
(``>=X.Y.0``) excludes ``X.Y.0.devN`` (PEP 440 dev releases sort *below* the final) and the
resolve becomes unsatisfiable. These tests lock in that all ``wfx`` forms -- bare and with
extras -- get the same exact dev pin.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import update_lf_base_dependency as mod


@pytest.fixture
def pyproject(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A throwaway pyproject whose wfx refs mirror src/backend/base/pyproject.toml."""
    content = (
        "[project]\n"
        "dependencies = [\n"
        '    "wfx~=1.11.0",\n'
        "]\n"
        "\n"
        "[project.optional-dependencies]\n"
        'cassandra = ["wfx[cassandra]~=1.11.0"]\n'
        "toolguard = [\"wfx[toolguard]~=1.11.0; sys_platform != 'win32'\"]\n"
        'beautifulsoup = ["wfx~=1.11.0"]\n'
    )
    path = tmp_path / "pyproject.toml"
    path.write_text(content, encoding="utf-8")
    # The script resolves paths relative to BASE_DIR; point it at tmp_path.
    monkeypatch.setattr(mod, "BASE_DIR", tmp_path)
    return path


def test_pins_bare_and_extras_wfx_to_exact_dev(pyproject: Path) -> None:
    mod.update_wfx_dep_in_base(pyproject.name, "1.11.0.dev26")
    result = pyproject.read_text(encoding="utf-8")

    # Every wfx reference -- bare and with extras -- is pinned to the exact dev version.
    assert '"wfx==1.11.0.dev26"' in result
    assert '"wfx[cassandra]==1.11.0.dev26"' in result
    assert "\"wfx[toolguard]==1.11.0.dev26; sys_platform != 'win32'\"" in result

    # No `~=` floor survives -- a surviving floor is exactly what makes the nightly
    # resolve unsatisfiable.
    assert "~=" not in result
    # Extras are preserved, never dropped.
    assert "[cassandra]" in result
    assert "[toolguard]" in result


def test_idempotent_on_already_pinned(pyproject: Path) -> None:
    mod.update_wfx_dep_in_base(pyproject.name, "1.11.0.dev26")
    once = pyproject.read_text(encoding="utf-8")
    mod.update_wfx_dep_in_base(pyproject.name, "1.11.0.dev26")
    twice = pyproject.read_text(encoding="utf-8")
    assert once == twice


def test_raises_when_no_wfx_dependency(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\ndependencies = ["primeagent-base~=1.11.0"]\n', encoding="utf-8")
    monkeypatch.setattr(mod, "BASE_DIR", tmp_path)
    with pytest.raises(ValueError, match="WFX dependency not found"):
        mod.update_wfx_dep_in_base(path.name, "1.11.0.dev26")


def test_pattern_skips_unrelated_packages(pyproject: Path) -> None:
    """Sibling packages whose names merely start with ``wfx`` must not be repinned."""
    extra = '    "wfx-bundles~=1.11.0",\n    "wfxthing~=1.11.0",\n'
    pyproject.write_text(pyproject.read_text(encoding="utf-8") + extra, encoding="utf-8")
    mod.update_wfx_dep_in_base(pyproject.name, "1.11.0.dev26")
    result = pyproject.read_text(encoding="utf-8")
    # The dedicated `wfx` distribution and its extras are repinned...
    assert '"wfx==1.11.0.dev26"' in result
    # ...but `wfx-bundles` / `wfxthing` keep their own floors untouched.
    assert re.search(r'"wfx-bundles~=1\.11\.0"', result)
    assert re.search(r'"wfxthing~=1\.11\.0"', result)


def test_root_base_pins_preserve_each_optional_extra(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(
        "[project]\n"
        'dependencies = ["primeagent-base~=1.12.0"]\n'
        "[project.optional-dependencies]\n"
        'audio = ["primeagent-base[audio]~=1.12.0"]\n'
        'postgresql = ["primeagent-base[postgresql]~=1.12.0"]\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "BASE_DIR", tmp_path)

    mod.update_base_dep(path.name, "1.12.0.dev26")

    result = path.read_text(encoding="utf-8")
    assert '"primeagent-base==1.12.0.dev26"' in result
    assert '"primeagent-base[audio]==1.12.0.dev26"' in result
    assert '"primeagent-base[postgresql]==1.12.0.dev26"' in result
