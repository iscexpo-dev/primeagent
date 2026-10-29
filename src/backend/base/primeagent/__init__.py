"""Primeagent backwards compatibility layer.

This module provides backwards compatibility by forwarding imports from
primeagent.* to wfx.* to maintain compatibility with existing code that
references the old primeagent module structure.
"""

from primeagent.helpers.windows_postgres_helper import configure_windows_postgres_event_loop

configure_windows_postgres_event_loop(source="package_init")

import importlib  # noqa: E402
import importlib.abc  # noqa: E402
import importlib.machinery  # noqa: E402
import importlib.util  # noqa: E402
import sys  # noqa: E402
from types import ModuleType  # noqa: E402
from typing import Any  # noqa: E402

# ---------------------------------------------------------------------------
# Dynamic ``primeagent.components.*`` -> ``wfx.components.*`` bridge
# ---------------------------------------------------------------------------
#
# Saved flows in the wild import their components via ``primeagent.components.<sub>``
# (``from primeagent.components.processing.converter import convert_to_dataframe``,
# ``import primeagent.components.knowledge_bases.retrieval``, etc.).  The wfx
# extraction moved every component module into ``wfx.components.*``; we
# previously kept a stack of physical shim files (one per subpackage)
# under ``src/backend/base/primeagent/components/`` to forward those imports.
# Maintaining one shim file per subpackage does not scale -- every new wfx
# component requires a parallel primeagent shim, and forgetting to add one
# silently breaks pre-existing flows at load time.
#
# Replace the physical-shim stack with a single meta path finder that
# dynamically resolves any ``primeagent.components.<rest>`` import to the
# corresponding ``wfx.components.<rest>`` module.  The finder returns the
# already-loaded wfx module from ``create_module`` so the primeagent- and
# wfx-prefixed names share a single underlying module object; class
# identity is preserved across the bridge (critical for ``isinstance``
# checks against types resolved through either path).
#
# Special-case overrides cover the few subpackages whose name diverged
# during the move (e.g. ``knowledge_bases`` -> ``files_and_knowledge``).


class _PrimeagentComponentsAliasLoader(importlib.abc.Loader):
    """Loader that fronts ``wfx.components.<rest>`` as ``primeagent.components.<rest>``.

    ``create_module`` returns the wfx module object directly so attribute
    access on either name resolves to the same backing module.
    ``exec_module`` is intentionally a no-op because the wfx module is
    already fully initialized by ``importlib.import_module`` inside
    ``create_module``.
    """

    def __init__(self, primeagent_name: str, wfx_name: str) -> None:
        self.primeagent_name = primeagent_name
        self.wfx_name = wfx_name

    def create_module(self, spec):  # noqa: ARG002 - protocol signature
        return importlib.import_module(self.wfx_name)

    def exec_module(self, module):  # noqa: ARG002 - module already initialised
        return None


class _PrimeagentComponentsAliasFinder(importlib.abc.MetaPathFinder):
    """Bridge ``primeagent.components.<rest>`` -> ``wfx.components.<rest>`` for arbitrary subpackages.

    Replaces a stack of per-subpackage physical shim files with a single
    dynamic resolver, so a new wfx component module never requires a
    parallel primeagent shim.  Saved flows that imported components via
    the legacy ``primeagent.components.*`` paths (and the integration tests
    that document the contract) continue to load without modification.
    """

    _BRIDGE_PREFIX = "primeagent.components"
    _WFX_PREFIX = "wfx.components"

    # First-segment renames applied when translating ``primeagent.components.<head>[.<tail>]``
    # to ``wfx.components.<renamed>[.<tail>]``.  ``knowledge_bases`` was
    # renamed to ``files_and_knowledge`` in wfx during the move; the
    # primeagent-side import path stays as ``knowledge_bases`` so the
    # already-shipped saved flows continue to resolve.
    _PACKAGE_OVERRIDES = {
        "knowledge_bases": "files_and_knowledge",
    }

    def find_spec(self, fullname, path=None, target=None):  # noqa: ARG002 - protocol signature
        if fullname != self._BRIDGE_PREFIX and not fullname.startswith(self._BRIDGE_PREFIX + "."):
            return None
        rel = fullname[len(self._BRIDGE_PREFIX) :].lstrip(".")
        if rel:
            head, _, tail = rel.partition(".")
            head = self._PACKAGE_OVERRIDES.get(head, head)
            wfx_name = f"{self._WFX_PREFIX}.{head}" + (f".{tail}" if tail else "")
        else:
            wfx_name = self._WFX_PREFIX
        try:
            wfx_spec = importlib.util.find_spec(wfx_name)
        except (ImportError, ValueError, ModuleNotFoundError, AttributeError):
            return None
        if wfx_spec is None:
            return None
        # Mirror the wfx target's package-ness so ``__path__`` is set
        # correctly on the alias and downstream ``import`` statements that
        # treat the alias as a package keep working.
        is_package = wfx_spec.submodule_search_locations is not None
        return importlib.machinery.ModuleSpec(
            fullname,
            _PrimeagentComponentsAliasLoader(fullname, wfx_name),
            is_package=is_package,
        )


class PrimeagentCompatibilityModule(ModuleType):
    """A module that forwards attribute access to the corresponding wfx module."""

    def __init__(self, name: str, wfx_module_name: str):
        super().__init__(name)
        self._wfx_module_name = wfx_module_name
        self._wfx_module = None

    def _get_wfx_module(self):
        """Lazily import and cache the wfx module."""
        if self._wfx_module is None:
            try:
                self._wfx_module = importlib.import_module(self._wfx_module_name)
            except ImportError as e:
                msg = f"Cannot import {self._wfx_module_name} for backwards compatibility with {self.__name__}"
                raise ImportError(msg) from e
        return self._wfx_module

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to the wfx module with caching."""
        wfx_module = self._get_wfx_module()
        try:
            attr = getattr(wfx_module, name)
        except AttributeError as e:
            msg = f"module '{self.__name__}' has no attribute '{name}'"
            raise AttributeError(msg) from e
        else:
            # Cache the attribute in our __dict__ for faster subsequent access
            setattr(self, name, attr)
            return attr

    def __dir__(self):
        """Return directory of the wfx module."""
        try:
            wfx_module = self._get_wfx_module()
            return dir(wfx_module)
        except ImportError:
            return []


def _setup_compatibility_modules():
    """Set up comprehensive compatibility modules for primeagent.base imports."""
    # First, set up the base attribute on this module (primeagent)
    current_module = sys.modules[__name__]

    # Install the dynamic ``primeagent.components.<rest>`` -> ``wfx.components.<rest>``
    # bridge BEFORE any explicit module_mappings entries are registered.  The
    # finder handles every subpackage (including ones added later when a new
    # bundle is extracted), so the explicit per-helper entries that used to
    # live in module_mappings are no longer needed here.
    if not any(isinstance(f, _PrimeagentComponentsAliasFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _PrimeagentComponentsAliasFinder())

    # Define all the modules we need to support
    module_mappings = {
        # Core base module
        "primeagent.base": "wfx.base",
        # Inputs module - critical for class identity
        "primeagent.inputs": "wfx.inputs",
        "primeagent.inputs.inputs": "wfx.inputs.inputs",
        # Schema modules - also critical for class identity
        "primeagent.schema": "wfx.schema",
        "primeagent.schema.data": "wfx.schema.data",
        "primeagent.schema.serialize": "wfx.schema.serialize",
        # Template modules
        "primeagent.template": "wfx.template",
        "primeagent.template.field": "wfx.template.field",
        "primeagent.template.field.base": "wfx.template.field.base",
        # ``primeagent.components.*`` is bridged dynamically by
        # ``_PrimeagentComponentsAliasFinder`` registered above, so no
        # entries are needed here.
        # Individual modules that exist in wfx
        "primeagent.base.agents": "wfx.base.agents",
        "primeagent.base.chains": "wfx.base.chains",
        "primeagent.base.data": "wfx.base.data",
        "primeagent.base.data.utils": "wfx.base.data.utils",
        "primeagent.base.document_transformers": "wfx.base.document_transformers",
        "primeagent.base.embeddings": "wfx.base.embeddings",
        "primeagent.base.flow_processing": "wfx.base.flow_processing",
        "primeagent.base.io": "wfx.base.io",
        "primeagent.base.io.chat": "wfx.base.io.chat",
        "primeagent.base.io.text": "wfx.base.io.text",
        "primeagent.base.langchain_utilities": "wfx.base.langchain_utilities",
        "primeagent.base.memory": "wfx.base.memory",
        "primeagent.base.models": "wfx.base.models",
        "primeagent.base.models.google_generative_ai_constants": "wfx.base.models.google_generative_ai_constants",
        "primeagent.base.models.openai_constants": "wfx.base.models.openai_constants",
        "primeagent.base.models.anthropic_constants": "wfx.base.models.anthropic_constants",
        "primeagent.base.models.aiml_constants": "wfx.base.models.aiml_constants",
        "primeagent.base.models.aws_constants": "wfx.base.models.aws_constants",
        "primeagent.base.models.groq_constants": "wfx.base.models.groq_constants",
        "primeagent.base.models.novita_constants": "wfx.base.models.novita_constants",
        "primeagent.base.models.ollama_constants": "wfx.base.models.ollama_constants",
        "primeagent.base.models.sambanova_constants": "wfx.base.models.sambanova_constants",
        "primeagent.base.models.cometapi_constants": "wfx.base.models.cometapi_constants",
        "primeagent.base.prompts": "wfx.base.prompts",
        "primeagent.base.prompts.api_utils": "wfx.base.prompts.api_utils",
        "primeagent.base.prompts.utils": "wfx.base.prompts.utils",
        "primeagent.base.textsplitters": "wfx.base.textsplitters",
        "primeagent.base.tools": "wfx.base.tools",
        "primeagent.base.vectorstores": "wfx.base.vectorstores",
    }

    # Create compatibility modules for each mapping
    for primeagent_name, wfx_name in module_mappings.items():
        if primeagent_name not in sys.modules:
            # Check if the wfx module exists
            try:
                spec = importlib.util.find_spec(wfx_name)
                if spec is not None:
                    # Create compatibility module
                    compat_module = PrimeagentCompatibilityModule(primeagent_name, wfx_name)
                    sys.modules[primeagent_name] = compat_module

                    # Set up the module hierarchy
                    parts = primeagent_name.split(".")
                    if len(parts) > 1:
                        parent_name = ".".join(parts[:-1])
                        parent_module = sys.modules.get(parent_name)
                        if parent_module is not None:
                            setattr(parent_module, parts[-1], compat_module)

                    # Special handling for top-level modules
                    if primeagent_name == "primeagent.base":
                        current_module.base = compat_module
                    elif primeagent_name == "primeagent.inputs":
                        current_module.inputs = compat_module
                    elif primeagent_name == "primeagent.schema":
                        current_module.schema = compat_module
                    elif primeagent_name == "primeagent.template":
                        current_module.template = compat_module
                    elif primeagent_name == "primeagent.components":
                        current_module.components = compat_module
            except (ImportError, ValueError):
                # Skip modules that don't exist in wfx
                continue

    # Handle modules that exist only in primeagent (like knowledge_bases)
    # These need special handling because they're not in wfx yet.
    # ``primeagent.components.knowledge_bases`` is no longer listed here:
    # ``_PrimeagentComponentsAliasFinder`` rewrites it to
    # ``wfx.components.files_and_knowledge`` via the override map and the
    # physical shim file used to live under ``components/knowledge_bases/``
    # has been removed.
    primeagent_only_modules = {
        "primeagent.base.data.kb_utils": "primeagent.base.data.kb_utils",
        "primeagent.base.knowledge_bases": "primeagent.base.knowledge_bases",
    }

    for primeagent_name in primeagent_only_modules:
        if primeagent_name not in sys.modules:
            try:
                # Try to find the actual physical module file
                from pathlib import Path

                base_dir = Path(__file__).parent

                if primeagent_name == "primeagent.base.data.kb_utils":
                    kb_utils_file = base_dir / "base" / "data" / "kb_utils.py"
                    if kb_utils_file.exists():
                        spec = importlib.util.spec_from_file_location(primeagent_name, kb_utils_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[primeagent_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("primeagent.base.data")
                            if parent_module is not None:
                                parent_module.kb_utils = module

                elif primeagent_name == "primeagent.base.knowledge_bases":
                    kb_dir = base_dir / "base" / "knowledge_bases"
                    kb_init_file = kb_dir / "__init__.py"
                    if kb_init_file.exists():
                        spec = importlib.util.spec_from_file_location(primeagent_name, kb_init_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[primeagent_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("primeagent.base")
                            if parent_module is not None:
                                parent_module.knowledge_bases = module

            except (ImportError, AttributeError):
                # If direct file loading fails, skip silently
                continue


# Set up all the compatibility modules
_setup_compatibility_modules()
