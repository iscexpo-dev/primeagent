"""Integration coverage for CLI command plugins on the Primeagent root app."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any

import typer
from wfx.cli import command_plugins
from typer.testing import CliRunner


@dataclass
class _FakeEntryPoint:
    name: str
    value: str
    target: Any

    def load(self) -> Any:
        return self.target


def test_primeagent_root_app_registers_discovered_plugin_commands(monkeypatch):
    import primeagent.__main__ as primeagent_main

    def register(app: typer.Typer) -> None:
        @app.command(name="fixture-plugin")
        def fixture_plugin() -> None:
            typer.echo("primeagent plugin")

    entry_point = _FakeEntryPoint("fixture", "plugins.fixture:register", register)

    with monkeypatch.context() as scoped_patch:
        scoped_patch.setattr(
            command_plugins.metadata,
            "entry_points",
            lambda *, group: [entry_point] if group == "primeagent.cli_commands" else [],
        )
        reloaded_main = importlib.reload(primeagent_main)
        result = CliRunner().invoke(reloaded_main.app, ["fixture-plugin"])

    importlib.reload(primeagent_main)

    assert result.exit_code == 0
    assert result.output == "primeagent plugin\n"
