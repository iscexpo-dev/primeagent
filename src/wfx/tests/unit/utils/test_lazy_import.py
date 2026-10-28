"""Contract tests for the stable lazy-import helper (BUNDLE_API surface).

``wfx.utils.lazy_import.import_mod`` is called by separately-installed bundle
packages from their ``__getattr__``-based ``__init__.py`` files, so its home,
name, and behavior are contract-stable (see BUNDLE_API.md).  The legacy
internal path ``wfx.components._importing`` must keep re-exporting the same
object for backward compatibility.
"""

from __future__ import annotations

import pytest


def test_legacy_path_reexports_the_same_object() -> None:
    """wfx.components._importing.import_mod IS wfx.utils.lazy_import.import_mod."""
    from wfx.components._importing import import_mod as legacy
    from wfx.utils.lazy_import import import_mod as canonical

    assert legacy is canonical
    assert canonical.__module__ == "wfx.utils.lazy_import"


def test_import_mod_attribute_from_module() -> None:
    """The (attr, module, package) form imports a submodule and pulls the attribute."""
    from wfx.utils.lazy_import import import_mod

    result = import_mod("import_mod", "lazy_import", "wfx.utils")
    assert callable(result)


def test_import_mod_package_form() -> None:
    """The module_name='__module__' form imports `.attr_name` from the package."""
    from wfx.utils.lazy_import import import_mod

    module = import_mod("lazy_import", "__module__", "wfx.utils")
    assert module.__name__ == "wfx.utils.lazy_import"


def test_missing_attribute_raises_attribute_error() -> None:
    """The package form converts ModuleNotFoundError to AttributeError (PEP 562 shape)."""
    from wfx.utils.lazy_import import import_mod

    with pytest.raises(AttributeError, match="no attribute"):
        import_mod("does_not_exist_xyz", "__module__", "wfx.utils")
