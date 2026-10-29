"""Sync the ``wfx`` runtime-dependency floor in every ``src/bundles/*`` package.

After a ``make patch v=X.Y.Z`` version bump, each bundle's ``wfx`` dependency
floor must track Primeagent/WFX's ``major.minor`` line: a bundle published from
the X.Y release is built against that wfx's BUNDLE_API surface, so it must be
guaranteed to resolve an wfx new enough to carry it.  Before the WFX 0.5.x ->
1.10.0 realignment (#13176) the generated floor was a flat ``wfx>=0.5.0`` with
no upper bound, which silently permitted resolving against the now-dead 0.5.x
line -- and neither pip nor uv flags the cross-line jump.

Pin form: ``wfx>=X.Y.0.dev0,<(X+1).0.0`` -- floored at the very first
pre-release of the current minor line, capped below the next wfx major.  The
``.dev0`` floor (not ``X.Y.0``) is load-bearing: nightlies off a release
branch are canonical ``X.Y.0.devN`` pre-releases, and PEP 440 sorts those
BELOW ``X.Y.0`` -- a plain ``>=X.Y.0`` floor makes the branch's own nightly
``wfx`` unresolvable against its own bundles (primeagent-base pins
``wfx==X.Y.0.devN`` exactly, so the resolver cannot back off).  ``X.Y.0.dev0``
is the lowest version PEP 440 admits in the line, so every devN / rcN / final
satisfies it while older minor lines stay excluded.  The cap is a coarse
install-time guard against an untested wfx major; fine-grained BUNDLE_API
compatibility is still enforced at load time by each ``extension.json``'s
``wfx.compat`` list against the running wfx's ``BUNDLE_API_VERSION`` (see
``src/wfx/src/wfx/extension/manifest.py``).

Idempotent: re-running with the same version is a no-op (so it is safe to call
unconditionally from ``make patch``, including patch releases within a minor
line where the floor does not move).  Because it runs unconditionally, the
rewrite is a RATCHET: a pin already narrower than the generated one is kept
(see ``ratchet_spec``), so a hand-tightened maintenance pin survives a
``make patch`` on its branch.  Only the bundle's ``"wfx<op>..."``
runtime dependency is rewritten -- self-references such as
``"wfx-docling[local]"`` and the legacy ``"wfx-nightly=="`` form are left
untouched (neither has a bare version operator immediately after ``wfx``).

Stdlib only, so it runs in any CI checkout (same constraint as the sibling
``scripts/migrate/port_bundle.py``).

Usage:
    python scripts/ci/sync_bundle_wfx_pin.py 1.10.0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# Matches a bundle's ``"wfx<op>VERSION[,<UPPER]"`` runtime dependency. The
# version operator immediately after ``wfx`` is what distinguishes the runtime
# dep from self-refs like ``"wfx-docling[local]"`` (a ``-`` follows ``wfx``)
# and the legacy ``"wfx-nightly=="`` form from the retired nightly bundle
# rename track (see src/bundles/NIGHTLY.md).
_WFX_DEP_PATTERN = re.compile(
    r'"wfx(?:>=|~=|==)[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*'
    r'(?:,\s*<[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*)?"'
)

# Parses the leading ``X.Y`` out of an ``X.Y.Z`` (optionally ``vX.Y.Z``) version.
_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.\d+")


# Parses a PEP 440 version into a sortable key.  Stdlib only (no ``packaging``),
# so this covers just the forms bundle pins actually use: a dotted release with
# an optional ``dev``/``a``/``b``/``rc``/``post`` suffix.
_PEP440_RE = re.compile(r"^(?P<rel>\d+(?:\.\d+)*)(?:\.?(?P<stage>post|dev|a|b|rc)(?P<n>\d+))?$")
_STAGE_ORDER = {"dev": 0, "a": 1, "b": 2, "rc": 3, "": 4, "post": 5}

# The canonical generated pin, ``wfx>=FLOOR,<CAP``.  Only pins already in this
# exact shape are ratcheted; legacy forms (``~=``, ``==``, uncapped) are still
# normalised wholesale.
_CANONICAL_PIN_RE = re.compile(
    r"^wfx>=(?P<floor>[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*)"
    r",\s*<(?P<cap>[\d.]+(?:\.(?:post|dev|a|b|rc)\d+)*)$"
)


def _version_key(version: str) -> tuple[tuple[int, ...], int, int]:
    """Sortable PEP 440 key.  ``1.12`` and ``1.12.0`` compare equal."""
    match = _PEP440_RE.match(version)
    if not match:
        msg = f"Unparseable version {version!r} in an wfx pin"
        raise ValueError(msg)
    release = [int(part) for part in match.group("rel").split(".")]
    release += [0] * (4 - len(release))
    return tuple(release[:4]), _STAGE_ORDER[match.group("stage") or ""], int(match.group("n") or 0)


def ratchet_spec(existing: str, generated: str) -> str:
    """Tighten-only merge of a bundle's existing ``wfx`` pin with the generated one.

    ``make patch`` calls this module unconditionally, so a hand-tightened pin
    has to survive it.  The 1.11.x maintenance bundles are pinned
    ``wfx>=1.11.6,<1.12`` -- deliberately narrower than the generated
    ``wfx>=1.11.0.dev0,<2.0.0`` -- because the 1.11 and 1.12 lines publish
    bundles into one PyPI name/number space.  Regenerating the coarse cap
    there would let a 1.11-line bundle satisfy a 1.12 install, and since the
    1.11 bundle numbers currently sort HIGHER, the resolver would prefer it:
    ``primeagent==1.12`` would silently install 1.11-line bundle code.  That is
    the same defect that made ``primeagent==1.11.6`` unresolvable, pointed the
    other way, and it fails silently instead of loudly.

    So take the intersection: the higher floor and the lower cap.

    The exception is a line move.  When the existing cap excludes the target
    line outright (a bundle pinned ``<1.12`` being synced to 1.12) the
    intersection would be empty, so the generated pin supersedes instead.
    """
    existing_match = _CANONICAL_PIN_RE.match(existing)
    generated_match = _CANONICAL_PIN_RE.match(generated)
    if not existing_match or not generated_match:
        return generated

    generated_floor = generated_match.group("floor")
    line_key = _version_key(".".join([*generated_floor.split(".")[:2], "0"]))
    if _version_key(existing_match.group("cap")) <= line_key:
        return generated

    floor = max(existing_match.group("floor"), generated_floor, key=_version_key)
    cap = min(existing_match.group("cap"), generated_match.group("cap"), key=_version_key)
    return f"wfx>={floor},<{cap}"


def wfx_floor_spec(version: str) -> str:
    """Return the bundle ``wfx`` dependency spec for a Primeagent/WFX version.

    ``"1.11.0"`` -> ``"wfx>=1.11.0.dev0,<2.0.0"`` (floor at the minor line's
    first pre-release so the branch's own ``X.Y.0.devN`` nightlies resolve --
    see the module docstring; cap below the next wfx major). A leading ``v``
    is tolerated.

    NOTE: this floor format is duplicated in ``scripts/migrate/port_bundle.py``
    (``_current_wfx_floor``) so each script stays standalone; keep them in step.
    """
    match = _VERSION_RE.match(version.lstrip("v"))
    if not match:
        msg = f"Unparseable version {version!r}; expected X.Y.Z"
        raise ValueError(msg)
    major, minor = int(match.group(1)), int(match.group(2))
    return f"wfx>={major}.{minor}.0.dev0,<{major + 1}.0.0"


def rewrite_wfx_dep(content: str, floor_spec: str) -> str:
    """Rewrite the bundle's ``wfx`` runtime dep toward ``floor_spec``. Idempotent.

    The write is ratcheted through ``ratchet_spec``, so an existing pin
    narrower than ``floor_spec`` is preserved rather than widened.

    Only the first (runtime) ``"wfx<op>..."`` specifier on a NON-comment line
    is touched; self-refs and the nightly form do not match
    ``_WFX_DEP_PATTERN``.  Comment lines are skipped because the
    ``port_bundle.py`` pyproject template quotes an example pin in a comment
    ABOVE the dependencies block -- a whole-text first-match rewrite would
    update the example and silently leave the real dep stale.
    """
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            continue
        new_line, n = _WFX_DEP_PATTERN.subn(
            lambda match: f'"{ratchet_spec(match.group(0)[1:-1], floor_spec)}"', line, count=1
        )
        if n:
            lines[i] = new_line
            return "".join(lines)
    return content


def sync_bundles(version: str, bundles_dir: Path) -> list[tuple[str, bool]]:
    """Rewrite the ``wfx`` floor in every ``src/bundles/*/pyproject.toml``.

    Returns ``(bundle_name, changed)`` tuples, sorted by bundle name.
    """
    floor_spec = wfx_floor_spec(version)
    results: list[tuple[str, bool]] = []
    for pyproject in sorted(bundles_dir.glob("*/pyproject.toml")):
        original = pyproject.read_text(encoding="utf-8")
        updated = rewrite_wfx_dep(original, floor_spec)
        if updated != original:
            pyproject.write_text(updated, encoding="utf-8")
        results.append((pyproject.parent.name, updated != original))
    return results


def main() -> None:
    """Entry point.

    Usage:
        sync_bundle_wfx_pin.py <version>

    ``version`` is the Primeagent/WFX release version (e.g. ``1.10.0``).
    """
    expected_args = 2
    if len(sys.argv) != expected_args:
        print("Usage: sync_bundle_wfx_pin.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    floor_spec = wfx_floor_spec(version)  # validates early
    bundles_dir = BASE_DIR / "src" / "bundles"
    if not bundles_dir.is_dir():
        print("No src/bundles directory; nothing to sync.")
        return

    print(f'Syncing bundle wfx pin -> "{floor_spec}"')
    for name, changed in sync_bundles(version, bundles_dir):
        print(f"  {'updated' if changed else 'unchanged'}: {name}")


if __name__ == "__main__":
    main()
