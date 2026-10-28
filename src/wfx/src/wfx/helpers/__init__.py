"""Helpers module for the wfx package.

This module automatically chooses between the full primeagent implementation
(when available) and the wfx implementation (when standalone).
"""

from wfx.utils.primeagent_utils import has_primeagent_memory

# Import the appropriate implementation
if has_primeagent_memory():
    try:
        # Import full primeagent implementation
        # Base Model
        from primeagent.helpers.base_model import (
            BaseModel,
            SchemaField,
            build_model_from_schema,
            coalesce_bool,
        )

        # Custom
        from primeagent.helpers.custom import (
            format_type,
        )

        # Data
        from primeagent.helpers.data import (
            clean_string,
            data_to_text,
            data_to_text_list,
            docs_to_data,
            safe_convert,
        )

        # Flow
        from primeagent.helpers.flow import (
            build_schema_from_inputs,
            get_arg_names,
            get_flow_by_id_or_name,
            get_flow_inputs,
            list_a2a_agents_by_flow_folder,
            list_flows,
            list_flows_by_flow_folder,
            list_flows_by_folder_id,
            load_flow,
            run_flow,
        )
    except ImportError:
        # Fallback to wfx implementation if primeagent import fails
        # Base Model
        from wfx.helpers.base_model import (
            BaseModel,
            SchemaField,
            build_model_from_schema,
            coalesce_bool,
        )

        # Custom
        from wfx.helpers.custom import (
            format_type,
        )

        # Data
        from wfx.helpers.data import (
            clean_string,
            data_to_text,
            data_to_text_list,
            docs_to_data,
            safe_convert,
        )

        # Flow
        from wfx.helpers.flow import (
            build_schema_from_inputs,
            get_arg_names,
            get_flow_by_id_or_name,
            get_flow_inputs,
            list_a2a_agents_by_flow_folder,
            list_flows,
            list_flows_by_flow_folder,
            list_flows_by_folder_id,
            load_flow,
            run_flow,
        )
else:
    # Use wfx implementation
    # Base Model
    from wfx.helpers.base_model import (
        BaseModel,
        SchemaField,
        build_model_from_schema,
        coalesce_bool,
    )

    # Custom
    from wfx.helpers.custom import (
        format_type,
    )

    # Data
    from wfx.helpers.data import (
        clean_string,
        data_to_text,
        data_to_text_list,
        docs_to_data,
        safe_convert,
    )

    # Flow
    from wfx.helpers.flow import (
        build_schema_from_inputs,
        get_arg_names,
        get_flow_by_id_or_name,
        get_flow_inputs,
        list_a2a_agents_by_flow_folder,
        list_flows,
        list_flows_by_flow_folder,
        list_flows_by_folder_id,
        load_flow,
        run_flow,
    )

# Export the available functions
__all__ = [
    "BaseModel",
    "SchemaField",
    "build_model_from_schema",
    "build_schema_from_inputs",
    "clean_string",
    "coalesce_bool",
    "data_to_text",
    "data_to_text_list",
    "docs_to_data",
    "format_type",
    "get_arg_names",
    "get_flow_by_id_or_name",
    "get_flow_inputs",
    "list_a2a_agents_by_flow_folder",
    "list_flows",
    "list_flows_by_flow_folder",
    "list_flows_by_folder_id",
    "load_flow",
    "run_flow",
    "safe_convert",
]
