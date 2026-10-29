"""Compatibility shim for the Policies component moved to ``wfx-toolguard``."""

try:
    from wfx_toolguard.components.models_and_agents.policies_component import PoliciesComponent
except ModuleNotFoundError as exc:
    if exc.name is not None and exc.name.partition(".")[0] != "wfx_toolguard":
        raise
    msg = (
        "The Policies component moved to the 'wfx-toolguard' distribution. "
        'Install it with `pip install "wfx[toolguard]"`.'
    )
    raise ModuleNotFoundError(msg) from exc

__all__ = ["PoliciesComponent"]
