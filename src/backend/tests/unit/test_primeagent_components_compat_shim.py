"""Tests for the dynamic ``primeagent.components.*`` -> ``wfx.components.*`` bridge.

Saved flows in the wild import their components via the legacy
``primeagent.components.<sub>.<leaf>`` paths (the integration test
``test_dynamic_import_integration.py`` documents this contract).  The
wfx extraction moved every component module into ``wfx.components.*``;
``primeagent/__init__.py`` installs a meta path finder that bridges the
two namespaces dynamically so saved flows keep loading without
modification.

This suite locks the contract:

    1. Generic prefix bridge: ``primeagent.components.<rest>`` resolves to
       ``wfx.components.<rest>`` for arbitrary subpackages and submodules,
       including new bundles extracted in the future.
    2. Renamed-package override: ``primeagent.components.knowledge_bases``
       (and any submodule under it) resolves to
       ``wfx.components.files_and_knowledge`` because the package was
       renamed during the move while the primeagent-side path stays for
       saved-flow compat.
    3. Class identity is preserved: a class loaded via the primeagent path
       is the same object as the one loaded via the wfx path, so
       ``isinstance`` checks across the bridge keep working.
"""

from __future__ import annotations

import importlib
import sys

import primeagent  # noqa: F401  -- triggers the meta finder install


def test_dotted_submodule_import_resolves() -> None:
    """``from primeagent.components.processing.converter import X`` works.

    Regression: the deletion of the physical ``primeagent/components/processing/converter.py``
    shim broke this import path before the dynamic bridge landed.
    """
    from primeagent.components.processing.converter import convert_to_dataframe

    # The bridge is a name alias, not a copy; ``__module__`` reflects the
    # underlying wfx location so debuggers / stack traces point at the
    # canonical source file.
    assert convert_to_dataframe.__module__ == "wfx.components.processing.converter"


def test_helpers_subpackage_imports() -> None:
    """``from primeagent.components.helpers import X`` works for any helper class."""
    from primeagent.components.helpers import CalculatorComponent

    assert CalculatorComponent.__module__.startswith("wfx.components.")


def test_knowledge_bases_override_resolves_to_files_and_knowledge() -> None:
    """``primeagent.components.knowledge_bases[.<rest>]`` -> ``wfx.components.files_and_knowledge[.<rest>]``.

    The wfx package was renamed during the move; the primeagent-side path
    stays as ``knowledge_bases`` so saved flows that imported via that
    name continue to resolve.
    """
    from primeagent.components.knowledge_bases.retrieval import KnowledgeBaseComponent

    assert KnowledgeBaseComponent.__module__ == "wfx.components.files_and_knowledge.retrieval"


def test_class_identity_preserved_across_bridge() -> None:
    """Same class is returned via ``primeagent.components.X`` and ``wfx.components.X``.

    Critical for ``isinstance`` checks against types resolved through
    either path -- e.g. a saved flow imports the legacy primeagent path
    while runtime code imports the wfx path; both must compare equal.
    """
    import primeagent.components.processing.converter as primeagent_module
    import wfx.components.processing.converter as wfx_module

    assert primeagent_module is wfx_module
    assert primeagent_module.convert_to_dataframe is wfx_module.convert_to_dataframe


def test_top_level_components_is_aliased_to_wfx_components() -> None:
    """``import primeagent.components`` resolves to the wfx package.

    Catches the case where the meta finder isn't installed yet when
    ``primeagent.components`` is first imported -- happens on cold imports
    in test runs that don't go through ``primeagent.__init__`` first.
    """
    import primeagent.components
    import wfx.components

    assert primeagent.components is wfx.components


def test_arbitrary_extracted_bundle_resolves_via_dynamic_bridge() -> None:
    """A bundle that exists in wfx but had no physical ``primeagent/components`` shim resolves.

    Regression-future: the previous shim layout required a parallel
    physical file per subpackage; forgetting to add one silently broke
    pre-existing flows.  The dynamic bridge means a new wfx component
    module is reachable via the legacy primeagent path immediately.
    """
    # Pick any subpackage under wfx.components that didn't have a
    # physical shim under primeagent/components/ before the deletion.
    target = "wfx.components.helpers.calculator_core"
    importlib.import_module(target)
    bridge = importlib.import_module("primeagent.components.helpers.calculator_core")
    assert bridge is sys.modules[target]
