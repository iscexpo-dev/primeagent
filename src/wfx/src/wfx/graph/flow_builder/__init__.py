"""Pure flow-building utilities for constructing Primeagent flows programmatically.

All functions operate on plain dicts — no I/O, no network, no global state.
"""

from wfx.graph.flow_builder.component import (
    add_component,
    configure_component,
    get_component,
    list_components,
    needs_server_update,
    remove_component,
)
from wfx.graph.flow_builder.connect import (
    add_connection,
    ensure_tool_mode_supported,
    list_connections,
    remove_connection,
)
from wfx.graph.flow_builder.flow import empty_flow, flow_graph_repr, flow_info, flow_to_spec_summary
from wfx.graph.flow_builder.layout import layout_flow
from wfx.graph.flow_builder.spec import parse_flow_spec

__all__ = [
    "add_component",
    "add_connection",
    "configure_component",
    "empty_flow",
    "ensure_tool_mode_supported",
    "flow_graph_repr",
    "flow_info",
    "flow_to_spec_summary",
    "get_component",
    "layout_flow",
    "list_components",
    "list_connections",
    "needs_server_update",
    "parse_flow_spec",
    "remove_component",
    "remove_connection",
]
