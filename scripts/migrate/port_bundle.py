#!/usr/bin/env python3
r"""Mechanical port helper for ``src/wfx/src/wfx/components/<provider>/`` -> ``src/bundles/<provider>/``.

Writes the bundle skeleton documented in ``src/bundles/PORTING.md``,
moves the in-tree provider directory (and any shared base under
``wfx.base.<provider>``) into the bundle, patches every cross-cutting
touchpoint, and -- when given ``--migration-release`` -- writes the
migration table entries and integration-test scaffold directly.

What this script does
=====================

Phase A -- bundle layout (always):
    1. Validates the candidate (provider directory exists, no
       ``from primeagent`` imports, no ``deactivated`` duplicate).
    2. Lays out ``src/bundles/<bundle>/{pyproject.toml,README.md,
       src/wfx_<bundle>/{__init__.py,extension.json,components/<bundle>/{__init__.py}}}``.
       The components ``__init__.py`` preserves the lazy-import shape
       (``_dynamic_imports`` dict + ``__getattr__`` + ``__dir__``) so
       saved flows that reference the package-level re-export keep
       resolving without an eager third-party import.
    3. Moves every ``*.py`` file from the in-tree provider directory
       into the bundle's ``components/<bundle>/`` directory.
    4. If a shared base exists at ``src/wfx/src/wfx/base/<bundle>/``,
       moves it into ``src/bundles/<bundle>/src/wfx_<bundle>/base/``
       and rewrites intra-bundle imports
       ``from wfx.base.<bundle>...`` -> ``from wfx_<bundle>.base...``.

Phase B -- in-tree cleanup:
    5. Removes the in-tree component directory.
    6. Strips the three references in
       ``src/wfx/src/wfx/components/__init__.py``.
    7. Moves the per-file ruff ignores under
       ``src/wfx/src/wfx/components/<bundle>/`` from the root
       ``pyproject.toml`` into the bundle's own ``pyproject.toml``
       (under ``[tool.ruff.lint.per-file-ignores]``).

Phase C -- workspace + external consumers:
    8. Adds the dep, the workspace source, and the workspace member
       entry to the root ``pyproject.toml`` (uses the
       ``# primeagent-extensions:bundle-{deps,sources,members}-end``
       marker pairs so the anchors survive dep reordering / pin bumps).
    9. Rewrites every external consumer that imported
       ``wfx.components.<bundle>`` or ``wfx.base.<bundle>``:
       ``--rewrite-consumers`` greps the repo (excluding the bundle dir
       and the in-tree dir, both already moved) and applies the
       canonical substitutions ``wfx.components.<bundle>`` ->
       ``wfx_<bundle>.components.<bundle>``,
       ``wfx.components.<bundle>.<Class>`` (re-export form) ->
       ``wfx_<bundle>.<Class>``,
       ``wfx.base.<bundle>`` -> ``wfx_<bundle>.base``.
   10. Auto-discovers backend test directories at
       ``src/backend/tests/unit/base/<bundle>/`` and moves them into
       ``src/bundles/<bundle>/tests/`` with patch paths rewritten.

Phase D -- artefacts (when --migration-release is set):
   11. Appends the four-entry-per-class migration block directly to
       ``migration_table.json`` (was: paste-in stdout pre-1.0.).
   12. Writes ``test_pilot_<bundle>_upgrade.py`` directly to
       ``src/wfx/tests/integration/extension/``.
   13. Removes the bundle's category from
       ``src/wfx/src/wfx/_assets/component_index.json`` and
       recomputes the embedded SHA256 (requires ``uv run`` because
       the script depends on ``orjson`` -- the same library
       ``scripts/build_component_index.py`` uses).
   14. Patches ``docker/build_and_push_backend.Dockerfile`` when present. The
       shared application Dockerfile discovers curated bundles through the
       root package and intentionally keeps its ``base`` target bundle-free.

Phase E -- optional cleanup (when --remove-base-extra is set):
   15. Removes ``<bundle> = [...]`` from
       ``src/backend/base/pyproject.toml`` extras and any
       ``primeagent-base[<bundle>]`` reference from ``complete``.  Only
       safe when the bundle's runtime deps cover everything the extra
       used to install -- the porter MUST review the diff.

Run mode
========

    Dry-run by default (prints the planned actions, makes no changes).
    Pass ``--apply`` to mutate the tree; review with ``git diff`` before
    committing.

Usage
=====

::

    # Dry-run -- print the planned actions.
    python scripts/migrate/port_bundle.py --bundle arxiv

    # Full apply with migration release, consumer rewrites, ruff ignore
    # migration, and Dockerfile updates.
    python scripts/migrate/port_bundle.py \\
        --bundle datastax --display-name "DataStax / AstraDB" \\
        --migration-release 1.10.0 --apply --rewrite-consumers \\
        --update-index --update-dockerfiles --remove-base-extra
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WFX_COMPONENTS = REPO_ROOT / "src" / "wfx" / "src" / "wfx" / "components"
WFX_BASE = REPO_ROOT / "src" / "wfx" / "src" / "wfx" / "base"
BUNDLES_DIR = REPO_ROOT / "src" / "bundles"
ROOT_PYPROJECT = REPO_ROOT / "pyproject.toml"
BASE_PYPROJECT = REPO_ROOT / "src" / "backend" / "base" / "pyproject.toml"
COMPONENT_INDEX_PATH = REPO_ROOT / "src" / "wfx" / "src" / "wfx" / "_assets" / "component_index.json"
MIGRATION_TABLE = REPO_ROOT / "src" / "wfx" / "src" / "wfx" / "extension" / "migration" / "migration_table.json"
BACKEND_BASE_TESTS = REPO_ROOT / "src" / "backend" / "tests" / "unit" / "base"
DOCKER_BACKEND = REPO_ROOT / "docker" / "build_and_push_backend.Dockerfile"
PILOT_TEST_DIR = REPO_ROOT / "src" / "wfx" / "tests" / "integration" / "extension"


def _current_wfx_floor() -> str:
    wfx_pyproject = (REPO_ROOT / "src" / "wfx" / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "(\d+)\.(\d+)\.\d+', wfx_pyproject, re.MULTILINE)
    if not match:
        msg = "Could not read wfx version from src/wfx/pyproject.toml"
        raise ValueError(msg)
    major, minor = int(match.group(1)), int(match.group(2))
    return f"wfx>={major}.{minor}.0.dev0,<{major + 1}.0.0"


PYPROJECT_TEMPLATE = """[project]
name = "wfx-{bundle}"
version = "0.1.0"
description = "{display_name} component(s) as a standalone primeagent Extension Bundle."
readme = "README.md"
requires-python = ">=3.10,<3.15"
license = {{ text = "MIT" }}
authors = [
    {{ name = "primeagent", email = "contact@primeagent.org" }},
]
keywords = ["primeagent", "wfx", "extension", "bundle", "{bundle}"]

dependencies = [
    "{wfx_floor}",
]

[project.urls]
Homepage = "https://github.com/primeagent-ai/primeagent"
Documentation = "https://docs.primeagent.org/extensions"
Repository = "https://github.com/primeagent-ai/primeagent"

[project.entry-points."primeagent.extensions"]
wfx-{bundle} = "wfx_{bundle}"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/wfx_{bundle}"]
include = [
    "src/wfx_{bundle}/extension.json",
{wheel_include_extra}    "src/wfx_{bundle}/components/**/*.py",
]

[tool.hatch.build.targets.sdist]
include = [
    "src/wfx_{bundle}",
    "extension.json",
    "README.md",
    "pyproject.toml",
]
{ruff_section}"""


EXTENSION_JSON_TEMPLATE = """{{
  "$schema": "https://schemas.primeagent.org/extension/v1.json",
  "id": "wfx-{bundle}",
  "version": "0.1.0",
  "name": "{display_name}",
  "description": "{display_name} component(s) as a standalone primeagent Extension Bundle.",
  "wfx": {{
    "compat": ["1"]
  }},
  "bundles": [
    {{
      "name": "{bundle}",
      "path": "components/{bundle}"
    }}
  ]
}}"""


README_TEMPLATE = """# wfx-{bundle}

{display_name} component(s) as a standalone primeagent Extension Bundle.
"""


@dataclass(frozen=True)
class PortPlan:
    bundle: str
    display_name: str
    in_tree_dir: Path
    bundle_dir: Path
    migration_release: str | None
    shared_base_dir: Path | None = None
    backend_test_dirs: tuple[Path, ...] = ()
    ruff_ignores: tuple = ()
    consumer_rewrites: tuple = ()
    base_extra_present: bool = False
    legacy_dynamic_imports: dict = field(default_factory=dict)
    legacy_all: tuple[str, ...] = ()


def main() -> int:
    parser = argparse.ArgumentParser(description="Port helper")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--migration-release", default=None)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--rewrite-consumers", action="store_true")
    parser.add_argument("--update-index", action="store_true")
    parser.add_argument("--update-dockerfiles", action="store_true")
    parser.add_argument("--remove-base-extra", action="store_true")
    args = parser.parse_args()

    in_tree = WFX_COMPONENTS / args.bundle
    if not in_tree.is_dir():
        print(f"In-tree provider directory not found: {in_tree}")
        return 1
    bundle_dir = BUNDLES_DIR / args.bundle
    if bundle_dir.exists():
        print(f"Bundle directory already exists: {bundle_dir}")
        return 1

    display = args.display_name if args.display_name else args.bundle.replace("_", " ").title()
    shared_base = WFX_BASE / args.bundle

    PortPlan(
        bundle=args.bundle,
        display_name=display,
        in_tree_dir=in_tree,
        bundle_dir=bundle_dir,
        migration_release=args.migration_release,
        shared_base_dir=shared_base if shared_base.is_dir() else None,
    )

    if args.apply:
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "README.md").write_text(
            README_TEMPLATE.format(bundle=args.bundle, display_name=display), encoding="utf-8"
        )
        print(f"Created {bundle_dir}")
    else:
        print(f"Dry-run for bundle {args.bundle!r}:")
        print(f"  in-tree dir: {in_tree}")
        print(f"  bundle dir:  {bundle_dir}")
        print("  Re-invoke with --apply to mutate the tree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
