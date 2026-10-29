"""V2 workflow contract layer shared by the primeagent backend and ``wfx serve``.

This package holds the protocol-agnostic pieces of the V2 workflow API:

    - ``adapters``: the ``StreamAdapter`` protocol, the ``primeagent``/``agui`` SSE
      adapters, and the registry (``get_stream_adapter`` / ``available_protocols``).
    - ``agui_translator``: translates EventManager events into AG-UI events.
    - ``converters``: parses ``WorkflowRunRequest`` and builds the structured
      ``WorkflowExecutionResponse``.

It depends only on ``wfx.schema.workflow`` and ``ag_ui`` (no primeagent imports),
so both runtimes consume one contract. The primeagent backend layers its stateful
"vehicle" (database, job queue, auth) on top.
"""
