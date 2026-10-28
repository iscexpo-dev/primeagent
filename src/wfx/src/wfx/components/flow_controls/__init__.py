from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wfx.components._importing import import_mod

if TYPE_CHECKING:
    from wfx.components.flow_controls.conditional_router import ConditionalRouterComponent
    from wfx.components.flow_controls.data_conditional_router import DataConditionalRouterComponent
    from wfx.components.flow_controls.flow_tool import FlowToolComponent
    from wfx.components.flow_controls.human_input import HumanInput
    from wfx.components.flow_controls.listen import ListenComponent
    from wfx.components.flow_controls.loop import LoopComponent
    from wfx.components.flow_controls.notify import NotifyComponent
    from wfx.components.flow_controls.pass_message import PassMessageComponent
    from wfx.components.flow_controls.run_flow import RunFlowComponent
    from wfx.components.flow_controls.sub_flow import SubFlowComponent

_dynamic_imports = {
    "ConditionalRouterComponent": "conditional_router",
    "DataConditionalRouterComponent": "data_conditional_router",
    "FlowToolComponent": "flow_tool",
    "HumanInput": "human_input",
    "ListenComponent": "listen",
    "LoopComponent": "loop",
    "NotifyComponent": "notify",
    "PassMessageComponent": "pass_message",
    "RunFlowComponent": "run_flow",
    "SubFlowComponent": "sub_flow",
}

__all__ = [
    "ConditionalRouterComponent",
    "DataConditionalRouterComponent",
    "FlowToolComponent",
    "HumanInput",
    "ListenComponent",
    "LoopComponent",
    "NotifyComponent",
    "PassMessageComponent",
    "RunFlowComponent",
    "SubFlowComponent",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import flow control components on attribute access."""
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
