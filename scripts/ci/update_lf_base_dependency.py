#!/usr/bin/env python

import re
import sys
from pathlib import Path

import packaging.version

BASE_DIR = Path(__file__).parent.parent.parent
ARGUMENT_NUMBER = 3


def update_base_dep(pyproject_path: str, new_version: str) -> None:
    """Pin every ``primeagent-base`` requirement in a consumer pyproject."""
    filepath = BASE_DIR / pyproject_path
    content = filepath.read_text(encoding="utf-8")

    # Updated pattern to handle PEP 440 version suffixes, extras (e.g., [complete]),
    # ~=, ==, and >= version specifiers, and both primeagent-base and primeagent-base-nightly names
    # Captures extras in group 2 to preserve them in each replacement.
    pattern = re.compile(
        r'("primeagent-base(?:-nightly)?((?:\[[^\]]+\])?)(?:~=|==|>=)[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*")'
    )

    # Check if the pattern is found
    match = pattern.search(content)
    if not match:
        msg = f'primeagent-base dependency not found in "{filepath}"'
        raise ValueError(msg)

    # Keep the canonical `primeagent-base` name; the exact `==<dev>` pin enables pre-release
    # resolution down the tree and keeps base in lockstep with the run.
    content = pattern.sub(
        lambda dependency: f'"primeagent-base{dependency.group(2) or ""}=={new_version}"',
        content,
    )
    filepath.write_text(content, encoding="utf-8")


def update_wfx_dep_in_base(pyproject_path: str, wfx_version: str) -> None:
    """Update the WFX dependency in primeagent-base pyproject.toml to use nightly version."""
    filepath = BASE_DIR / pyproject_path
    content = filepath.read_text(encoding="utf-8")

    # Updated pattern to handle PEP 440 version suffixes, both ~= and == version specifiers,
    # both wfx and wfx-nightly names, extras (e.g. wfx[cassandra], wfx[toolguard]), and
    # trailing markers (e.g. `; sys_platform != 'win32'`).
    # The extras group (1) MUST be preserved: base's `[complete]` extra pulls these
    # `wfx[extra]` references, and if they keep a `~=X.Y.0` floor while base's bare `wfx`
    # dep is pinned to `==X.Y.0.devN`, the floor (>=X.Y.0) excludes the dev release and
    # the nightly resolve becomes unsatisfiable.
    version_pattern = r"[0-9]+(?:\.[0-9]+)*(?:\.(?:post|dev|a|b|rc)\d+)*"
    pattern = re.compile(rf'"wfx(?:-nightly)?((?:\[[^\]]+\])?)(?:~=|==){version_pattern}([^"]*)"')
    # Pin base's wfx dep to the exact canonical dev version (single `wfx` distribution, no
    # `wfx-nightly`), so there is no `wfx` vs `wfx-nightly` install collision with the bundles.

    # Check if the pattern is found
    if not pattern.search(content):
        msg = f'WFX dependency not found in "{filepath}"'
        raise ValueError(msg)

    # Replace each match, preserving its own extras and environment marker.
    content = pattern.sub(lambda m: f'"wfx{m.group(1)}=={wfx_version}{m.group(2)}"', content)
    filepath.write_text(content, encoding="utf-8")


def verify_pep440(version):
    """Verify if version is PEP440 compliant.

    https://github.com/pypa/packaging/blob/16.7/packaging/version.py#L191
    """
    return packaging.version.Version(version)


def main() -> None:
    if len(sys.argv) != ARGUMENT_NUMBER:
        msg = "Usage: update_lf_base_dependency.py <base_version> <wfx_version>"
        raise ValueError(msg)
    base_version = sys.argv[1]
    wfx_version = sys.argv[2]

    # Strip "v" prefix from versions if present
    base_version = base_version.removeprefix("v")
    wfx_version = wfx_version.removeprefix("v")

    verify_pep440(base_version)
    verify_pep440(wfx_version)

    # Main delegates directly to the product-aligned base distribution.
    update_base_dep("pyproject.toml", base_version)

    # Update WFX dependency in primeagent-base
    update_wfx_dep_in_base("src/backend/base/pyproject.toml", wfx_version)


if __name__ == "__main__":
    main()
