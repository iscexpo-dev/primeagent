"""Agentic runtime validation must reject transitive pickle loading before execution."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from primeagent.agentic.helpers.validation import validate_component_runtime


@pytest.mark.asyncio
async def test_runtime_validation_rejects_pandas_pickle_before_component_build():
    code = """
import pandas as pd
from wfx.custom import Component
from wfx.io import Output

class DataLoader(Component):
    outputs = [Output(name="result", method="load")]

    def load(self):
        return pd.read_pickle(self.payload)
"""
    settings = SimpleNamespace(settings=SimpleNamespace(allow_custom_components=True))
    with (
        patch("wfx.services.deps.get_settings_service", return_value=settings),
        patch("wfx.custom.utils.build_custom_component_template") as build_component,
    ):
        result = await validate_component_runtime(code, user_id="user")

    assert result is not None
    assert "security validation" in result.lower()
    assert "pandas.read_pickle" in result
    build_component.assert_not_called()
