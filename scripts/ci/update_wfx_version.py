"""Update the canonical ``wfx`` package (and its SDK dep) for nightly builds.

The nightly publishes ``wfx`` and ``primeagent-sdk`` under their CANONICAL names as ``.devN``
pre-releases -- it does NOT rename them to ``wfx-nightly`` / ``primeagent-sdk-nightly``, and it does
NOT give the ``src/bundles/*`` packages their own nightly track. The stable ``wfx-*`` bundles
(pinning ``wfx>=X.Y.0,<(X+1).0.0``) then resolve against the single canonical ``wfx`` distribution,
so there is no ``wfx`` vs ``wfx-nightly`` install collision. See ``src/bundles/NIGHTLY.md``.

This script therefore only (a) sets ``wfx``'s version to the nightly ``.devN`` and (b) re-pins
wfx's ``primeagent-sdk`` dependency to the exact canonical dev version.
"""

import re
import sys
from pathlib import Path

from update_component_index_version import update_component_index_version
from update_pyproject_version import update_pyproject_version

# Add the current directory to the path so we can import the other scripts
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

BASE_DIR = Path(__file__).parent.parent.parent
COMPONENT_INDEX_PATH = Path("src/wfx/src/wfx/_assets/component_index.json")


def update_sdk_dependency_in_wfx(pyproject_path: str, sdk_version: str) -> None:
    """Pin wfx's ``primeagent-sdk`` dependency to the exact canonical dev version.

    An exact ``==<dev>`` pin keeps the SDK in lockstep with the wfx built in the same run and,
    because it names a pre-release explicitly, enables pre-release resolution for ``primeagent-sdk``
    down the dependency tree without requiring ``--pre``.
    """
    filepath = BASE_DIR / pyproject_path
    content = filepath.read_text(encoding="utf-8")

    pattern = re.compile(r'"primeagent-sdk(?:-nightly)?(?:==|~=|>=)[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*"')
    replacement = f'"primeagent-sdk=={sdk_version}"'

    if not pattern.search(content):
        msg = f"SDK dependency not found in {filepath}"
        raise ValueError(msg)

    content = pattern.sub(replacement, content)
    filepath.write_text(content, encoding="utf-8")


def update_wfx_for_nightly(wfx_tag: str, sdk_tag: str):
    """Update the canonical ``wfx`` package for a nightly build.

    Args:
        wfx_tag: The nightly tag for WFX (e.g., "v1.11.0.dev0").
        sdk_tag: The nightly tag for the SDK (e.g., "v0.1.0.dev0").
    """
    wfx_pyproject_path = "src/wfx/pyproject.toml"

    # Set the version (strip 'v' prefix if present); the package keeps its canonical `wfx` name.
    version = wfx_tag.lstrip("v")
    update_pyproject_version(wfx_pyproject_path, version)

    # Re-pin wfx's SDK dependency to the exact canonical dev version.
    sdk_version = sdk_tag.lstrip("v")
    update_sdk_dependency_in_wfx(wfx_pyproject_path, sdk_version)

    # The runtime rejects a prebuilt index whose version differs from the
    # installed WFX distribution. Nightly version rewrites must therefore keep
    # the bundled index and its integrity hash in lockstep with pyproject.toml.
    update_component_index_version(BASE_DIR / COMPONENT_INDEX_PATH, version)

    print(f"Updated wfx to nightly version {version}")


def main():
    """Update WFX for nightly builds.

    Usage:
    update_wfx_version.py <wfx_tag> <sdk_tag>
    """
    expected_args = 3
    if len(sys.argv) != expected_args:
        print("Usage: update_wfx_version.py <wfx_tag> <sdk_tag>")
        sys.exit(1)

    wfx_tag = sys.argv[1]
    sdk_tag = sys.argv[2]
    update_wfx_for_nightly(wfx_tag, sdk_tag)


if __name__ == "__main__":
    main()
