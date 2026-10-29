import asyncio

import pytest
from wfx.components.input_output import ChatInput, ChatOutput
from wfx.execution import (
    Coordinator,
    ExecutorRegistry,
    set_default_coordinator,
)
from wfx.execution.executor import Executor
from wfx.execution.types import RunComplete
from wfx.graph import Graph
from wfx.graph.schema import RunOutputs


@pytest.mark.asyncio
async def test_arun_dispatches_through_coordinator(simple_graph):
    units_seen: list[object] = []

    class Recording(Executor):
        kind = "in-process"

        async def execute(self, unit):
            units_seen.append(unit)
            yield RunComplete(outputs=[])

    registry = ExecutorRegistry()
    registry.register(Recording())
    set_default_coordinator(Coordinator(registry=registry))

    await simple_graph.arun(inputs=[{"input_value": "hi"}])
    assert len(units_seen) == 1
    seen = units_seen[0]
    assert seen.inputs == [{"input_value": "hi"}]
    assert seen.runtime_options.get("_use_arun_legacy") is True


@pytest.mark.asyncio
async def test_arun_returns_run_outputs_shape(simple_graph):
    outputs = await simple_graph.arun(inputs=[{"input_value": "hi"}])
    assert isinstance(outputs, list)
    assert len(outputs) == 1
    assert isinstance(outputs[0], RunOutputs)
    assert outputs[0].inputs == {"input_value": "hi"}


@pytest.mark.asyncio
async def test_arun_concurrent_on_separate_graphs_keep_options_isolated():
    """Concurrent arun on separate Graph instances keeps kwargs isolated."""
    seen: list[str] = []

    async def patched(*, inputs, **kwargs):  # noqa: ARG001
        seen.append(kwargs.get("session_id") or "")
        await asyncio.sleep(0.01)
        return []

    def _build():
        ci = ChatInput(_id="chat_input")
        ci.set(should_store_message=False)
        co = ChatOutput(input_value="test", _id="chat_output")
        co.set(sender_name=ci.message_response)
        return Graph(ci, co)

    async def run_with(session_id):
        graph = _build()
        graph._arun_legacy = patched
        await graph.arun(inputs=[{"input_value": session_id}], session_id=session_id)

    await asyncio.gather(run_with("A"), run_with("B"))
    assert sorted(seen) == ["A", "B"]
