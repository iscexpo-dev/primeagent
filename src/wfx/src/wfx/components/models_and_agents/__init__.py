from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING, Any

from wfx.components._importing import import_mod

if TYPE_CHECKING:
    from wfx.components.models_and_agents.a2a_agent import A2AAgentComponent
    from wfx.components.models_and_agents.agent import AgentComponent
    from wfx.components.models_and_agents.embedding_model import EmbeddingModelComponent
    from wfx.components.models_and_agents.language_model import LanguageModelComponent
    from wfx.components.models_and_agents.mcp_component import MCPToolsComponent
    from wfx.components.models_and_agents.memory import MemoryComponent
    from wfx.components.models_and_agents.policies_component import PoliciesComponent
    from wfx.components.models_and_agents.prompt import PromptComponent

_dynamic_imports = {
    "A2AAgentComponent": "a2a_agent",
    "AgentComponent": "agent",
    "EmbeddingModelComponent": "embedding_model",
    "LanguageModelComponent": "language_model",
    "MCPToolsComponent": "mcp_component",
    "MemoryComponent": "memory",
    "PoliciesComponent": "policies_component",
    "PromptComponent": "prompt",
}

__all__ = [
    "A2AAgentComponent",
    "AgentComponent",
    "EmbeddingModelComponent",
    "LanguageModelComponent",
    "MCPToolsComponent",
    "MemoryComponent",
    "PromptComponent",
]

# ``wfx.components.models`` re-exports this module with ``import *``. Keep the
# legacy package-level Policies export available when the extension is
# installed, but do not make a plain WFX/base import resolve the compatibility
# shim and fail just because ``wfx-toolguard`` is intentionally absent.
if find_spec("wfx_toolguard") is not None:
    __all__ += ["PoliciesComponent"]


def __getattr__(attr_name: str) -> Any:
    """Lazily import model and agent components on attribute access."""
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
