"""WFX CLI entry point."""

from importlib.metadata import version as _pkg_version

import typer

from wfx.cli._authoring_commands import register as _register_authoring
from wfx.cli._extension_commands import register as _register_extension
from wfx.cli._observability_commands import register as _register_observability
from wfx.cli._prewarm_commands import register as _register_prewarm
from wfx.cli._remote_commands import register as _register_remote
from wfx.cli._running_commands import register as _register_running
from wfx.cli._setup_commands import register as _register_setup
from wfx.cli._upgrade_commands import register as _register_upgrade


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"wfx {_pkg_version('wfx')}")
        raise typer.Exit(0)


app = typer.Typer(
    name="wfx",
    help="wfx - Primeagent Executor",
    add_completion=False,
)


@app.callback()
def _app_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show the wfx version and exit.",
        is_eager=True,
        callback=_version_callback,
    ),
) -> None:
    """Wfx - Primeagent Executor."""


# Register command groups (order determines help-panel ordering)
_register_setup(app)
_register_observability(app)
_register_prewarm(app)
_register_authoring(app)
_register_upgrade(app)
_register_extension(app)
_register_running(app)
_register_remote(app)


def main():
    """Main entry point for the WFX CLI."""
    app()


if __name__ == "__main__":
    main()
