from typing import Final

DEFAULT_SEGMENT_WRITE_KEY: Final = ""

IBM_PRODUCT_PROPERTIES: Final = {
    "UT30": "30AS5",
    "productCode": "WW3151",
    "productCodeType": "WWPC",
    "productPlanName": "opensource",
    "productPlanType": "freemium",
    "productTitle": "Primeagent",
}

IBM_COMMON_EVENT_MAP: Final[dict[str, tuple[str, str | None]]] = {
    "version": ("Started Process", "Primeagent"),
    "run": ("Ran Process", "Primeagent Flow"),
    "deployment": ("Ran Process", "Primeagent Deployment"),
    "integration_action": ("Ran Process", "Primeagent Integration"),
    "deployment_provider": ("Ran Process", "Primeagent Deployment Provider"),
    "deployment_run": ("Ran Process", "Primeagent Deployment"),
    "shutdown": ("Ended Process", "Primeagent"),
    "email": ("UI Interaction", None),
    "playground": ("Ran Process", "Primeagent Playground"),
    "component": ("Ran Process", "Primeagent Component"),
    "component_inputs": ("Ran Process", "Primeagent Component Input"),
    "component_index": ("Ran Process", "Primeagent Component Index"),
    "exception": ("Ended Process", "Primeagent Exception"),
    "mcp_tool": ("Ran Process", "Primeagent MCP Tool"),
}


def get_ibm_common_event(path: str | None) -> tuple[str, str | None, str]:
    legacy_event = path or "version"
    event, process_type = IBM_COMMON_EVENT_MAP.get(
        legacy_event,
        ("Ran Process", f"Primeagent {legacy_event.replace('_', ' ').title()}"),
    )
    return event, process_type, legacy_event
