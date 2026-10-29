"""Tests for release-wheel selection used by Docker builds."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from scripts.ci.install_release_wheels import _restore_frontend, _select_wheels, install_release_wheels


def _write_wheel(directory: Path, name: str, version: str) -> None:
    normalized_name = name.replace("-", "_")
    wheel_path = directory / f"{normalized_name}-{version}-py3-none-any.whl"
    metadata_path = f"{normalized_name}-{version}.dist-info/METADATA"
    with zipfile.ZipFile(wheel_path, "w") as archive:
        archive.writestr(metadata_path, f"Metadata-Version: 2.4\nName: {name}\nVersion: {version}\n")


def test_main_selects_every_release_artifact(tmp_path: Path) -> None:
    _write_wheel(tmp_path, "primeagent", "1.11.0rc5")
    _write_wheel(tmp_path, "primeagent-base", "0.11.0rc5")
    _write_wheel(tmp_path, "wfx", "1.11.0rc5")
    _write_wheel(tmp_path, "primeagent-sdk", "0.3.0rc5")
    _write_wheel(tmp_path, "wfx-arxiv", "0.1.3rc5")

    wheels = _select_wheels(tmp_path, "main")

    assert {wheel.name: wheel.version for wheel in wheels} == {
        "primeagent": "1.11.0rc5",
        "primeagent-base": "0.11.0rc5",
        "primeagent-sdk": "0.3.0rc5",
        "wfx": "1.11.0rc5",
        "wfx-arxiv": "0.1.3rc5",
    }


def test_base_excludes_main_and_bundle_wheels(tmp_path: Path) -> None:
    _write_wheel(tmp_path, "primeagent", "1.11.0rc5")
    _write_wheel(tmp_path, "primeagent-base", "0.11.0rc5")
    _write_wheel(tmp_path, "primeagent-sdk", "0.3.0rc5")
    _write_wheel(tmp_path, "wfx", "1.11.0rc5")
    _write_wheel(tmp_path, "primeagent-sdk", "0.3.0rc5")
    _write_wheel(tmp_path, "wfx-arxiv", "0.1.3rc5")

    wheels = _select_wheels(tmp_path, "base")

    assert {wheel.name for wheel in wheels} == {"primeagent-base", "primeagent-sdk", "wfx"}


def test_missing_required_wheel_fails_closed(tmp_path: Path) -> None:
    _write_wheel(tmp_path, "primeagent-base", "0.11.0rc5")

    with pytest.raises(ValueError, match="missing required main wheels"):
        _select_wheels(tmp_path, "main")


def test_duplicate_release_wheels_fail_closed(tmp_path: Path) -> None:
    _write_wheel(tmp_path, "primeagent", "1.11.0rc4")
    _write_wheel(tmp_path, "primeagent", "1.11.0rc5")
    _write_wheel(tmp_path, "primeagent-base", "0.11.0rc5")
    _write_wheel(tmp_path, "wfx", "1.11.0rc5")

    with pytest.raises(ValueError, match="Duplicate release wheels for primeagent"):
        _select_wheels(tmp_path, "main")


def test_install_release_wheels_installs_only_target_profile_and_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_wheel(tmp_path, "primeagent", "1.11.0rc5")
    _write_wheel(tmp_path, "primeagent-base", "0.11.0rc5")
    _write_wheel(tmp_path, "primeagent-sdk", "0.3.0rc5")
    _write_wheel(tmp_path, "wfx", "1.11.0rc5")
    _write_wheel(tmp_path, "wfx-firecrawl", "0.1.1")
    _write_wheel(tmp_path, "wfx-duckduckgo", "0.1.3")
    python = tmp_path / "venv" / "bin" / "python"
    uv = tmp_path / "bin" / "uv"
    commands: list[tuple[list[object], bool]] = []
    profile_commands: list[list[object]] = []

    def record_run(command: list[object], *, check: bool) -> None:
        commands.append((command, check))

    def installed_profile(command: list[object], **_kwargs: object) -> str:
        profile_commands.append(command)
        return json.dumps(["primeagent", "primeagent-base", "wfx", "wfx-firecrawl"])

    monkeypatch.setattr("scripts.ci.install_release_wheels._find_uv", lambda: str(uv))
    monkeypatch.setattr("scripts.ci.install_release_wheels.subprocess.run", record_run)
    monkeypatch.setattr("scripts.ci.install_release_wheels.subprocess.check_output", installed_profile)

    install_release_wheels(tmp_path, python, "main")

    assert profile_commands[0][:3] == [python, "-I", "-c"]
    assert len(commands) == 3
    assert all(check for _, check in commands)
    install_command, verify_command, check_command = (command for command, _ in commands)
    assert install_command[:7] == [
        str(uv),
        "pip",
        "install",
        "--python",
        str(python),
        "--no-deps",
        "--force-reinstall",
    ]
    assert {Path(str(path)).name for path in install_command[7:]} == {
        "primeagent-1.11.0rc5-py3-none-any.whl",
        "primeagent_base-0.11.0rc5-py3-none-any.whl",
        "primeagent_sdk-0.3.0rc5-py3-none-any.whl",
        "wfx-1.11.0rc5-py3-none-any.whl",
        "wfx_firecrawl-0.1.1-py3-none-any.whl",
    }
    assert verify_command[:2] == [python, "-c"]
    assert "assert actual == expected" in str(verify_command[2])
    assert json.loads(str(verify_command[3])) == {
        "primeagent": "1.11.0rc5",
        "primeagent-base": "0.11.0rc5",
        "primeagent-sdk": "0.3.0rc5",
        "wfx": "1.11.0rc5",
        "wfx-firecrawl": "0.1.1",
    }
    assert check_command == [str(uv), "pip", "check", "--python", str(python)]


def test_install_release_wheels_rejects_malformed_target_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_wheel(tmp_path, "primeagent", "1.11.0rc5")
    _write_wheel(tmp_path, "primeagent-base", "0.11.0rc5")
    _write_wheel(tmp_path, "wfx", "1.11.0rc5")
    monkeypatch.setattr(
        "scripts.ci.install_release_wheels.subprocess.check_output",
        lambda *_args, **_kwargs: json.dumps({"primeagent": "1.11.0rc5"}),
    )

    with pytest.raises(ValueError, match="Expected installed distribution names as a JSON string list"):
        install_release_wheels(tmp_path, tmp_path / "venv" / "bin" / "python", "main")


def test_install_release_wheels_requires_uv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_wheel(tmp_path, "primeagent", "1.11.0rc5")
    _write_wheel(tmp_path, "primeagent-base", "0.11.0rc5")
    _write_wheel(tmp_path, "wfx", "1.11.0rc5")
    monkeypatch.setattr(
        "scripts.ci.install_release_wheels.subprocess.check_output",
        lambda *_args, **_kwargs: json.dumps(["primeagent", "primeagent-base", "wfx"]),
    )
    monkeypatch.setattr("scripts.ci.install_release_wheels.shutil.which", lambda _name: None)

    with pytest.raises(FileNotFoundError, match="uv is required"):
        install_release_wheels(tmp_path, tmp_path / "venv" / "bin" / "python", "main")


def test_install_release_wheels_without_artifacts_is_a_noop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[list[object]] = []
    monkeypatch.setattr(
        "scripts.ci.install_release_wheels.subprocess.run",
        lambda command, **_kwargs: commands.append(command),
    )

    install_release_wheels(tmp_path, tmp_path / "python", "main")

    assert commands == []


def test_restore_frontend_replaces_wheel_assets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    frontend_source = tmp_path / "built-frontend"
    frontend_source.mkdir()
    (frontend_source / "index.html").write_text("docker build", encoding="utf-8")
    package_dir = tmp_path / "site-packages" / "primeagent"
    installed_frontend = package_dir / "frontend"
    installed_frontend.mkdir(parents=True)
    (installed_frontend / "index.html").write_text("wheel build", encoding="utf-8")

    commands: list[list[object]] = []

    def find_installed_package(command: list[object], **_kwargs: object) -> str:
        commands.append(command)
        return str(package_dir)

    monkeypatch.setattr(
        "scripts.ci.install_release_wheels.subprocess.check_output",
        find_installed_package,
    )

    python = tmp_path / "python"
    _restore_frontend(python, frontend_source)

    assert commands[0][:3] == [python, "-I", "-c"]
    assert (installed_frontend / "index.html").read_text(encoding="utf-8") == "docker build"


def test_restore_frontend_rejects_source_target_collision(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    package_dir = tmp_path / "primeagent"
    frontend_source = package_dir / "frontend"
    frontend_source.mkdir(parents=True)
    (frontend_source / "index.html").write_text("docker build", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.ci.install_release_wheels.subprocess.check_output",
        lambda *_args, **_kwargs: str(package_dir),
    )

    with pytest.raises(ValueError, match="must be different"):
        _restore_frontend(tmp_path / "python", frontend_source)

    assert (frontend_source / "index.html").read_text(encoding="utf-8") == "docker build"
