"""Processing components for primeagent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wfx.components._importing import import_mod

if TYPE_CHECKING:
    from wfx.components.processing.combine_text import CombineTextComponent
    from wfx.components.processing.converter import TypeConverterComponent
    from wfx.components.processing.create_list import CreateListComponent
    from wfx.components.processing.data_operations import DataOperationsComponent
    from wfx.components.processing.dataframe_operations import DataFrameOperationsComponent
    from wfx.components.processing.json_cleaner import JSONCleaner
    from wfx.components.processing.operations import OperationsComponent
    from wfx.components.processing.output_parser import OutputParserComponent
    from wfx.components.processing.parse_data import ParseDataComponent
    from wfx.components.processing.parser import ParserComponent
    from wfx.components.processing.regex import RegexExtractorComponent
    from wfx.components.processing.split_text import SplitTextComponent
    from wfx.components.processing.store_message import MessageStoreComponent

_dynamic_imports = {
    "CombineTextComponent": "combine_text",
    "TypeConverterComponent": "converter",
    "CreateListComponent": "create_list",
    "DataOperationsComponent": "data_operations",
    "DataFrameOperationsComponent": "dataframe_operations",
    "JSONCleaner": "json_cleaner",
    "OperationsComponent": "operations",
    "OutputParserComponent": "output_parser",
    "ParseDataComponent": "parse_data",
    "ParserComponent": "parser",
    "RegexExtractorComponent": "regex",
    "SplitTextComponent": "split_text",
    "MessageStoreComponent": "store_message",
}

__all__ = [
    "CombineTextComponent",
    "CreateListComponent",
    "DataFrameOperationsComponent",
    "DataOperationsComponent",
    "JSONCleaner",
    "MessageStoreComponent",
    "OperationsComponent",
    "OutputParserComponent",
    "ParseDataComponent",
    "ParserComponent",
    "RegexExtractorComponent",
    "SplitTextComponent",
    "TypeConverterComponent",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import processing components on attribute access."""
    if attr_name not in _dynamic_imports:
        msg = f"module '{__name__}' has no attribute '{attr_name}'"
        raise AttributeError(msg)
    try:
        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        msg = f"Could not import '{attr_name}' from '{__name__}': {e}"
        raise AttributeError(msg) from e
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
