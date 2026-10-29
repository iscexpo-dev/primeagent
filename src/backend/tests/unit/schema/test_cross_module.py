"""Unit tests for cross-module isinstance functionality.

These tests verify that isinstance checks work correctly when classes are
re-exported from different modules (e.g., wfx.schema.Message vs primeagent.schema.Message).
"""

from primeagent.schema import Data as PrimeagentData
from primeagent.schema import Message as PrimeagentMessage
from wfx.schema.data import Data as WfxData
from wfx.schema.message import Message as WfxMessage


class TestDuckTypingData:
    """Tests for duck-typing Data class across module boundaries."""

    def test_wfx_data_isinstance_primeagent_data(self):
        """Test that wfx.Data instance is recognized as primeagent.Data."""
        wfx_data = WfxData(data={"key": "value"})
        assert isinstance(wfx_data, PrimeagentData)

    def test_primeagent_data_isinstance_wfx_data(self):
        """Test that primeagent.Data instance is recognized as wfx.Data."""
        primeagent_data = PrimeagentData(data={"key": "value"})
        assert isinstance(primeagent_data, WfxData)

    def test_data_equality_across_modules(self):
        """Test that Data objects from different modules are equal."""
        wfx_data = WfxData(data={"key": "value"})
        primeagent_data = PrimeagentData(data={"key": "value"})
        assert wfx_data == primeagent_data

    def test_data_interchangeable_in_functions(self):
        """Test that Data from different modules work interchangeably."""

        def process_data(data: PrimeagentData) -> str:
            return data.get_text()

        wfx_data = WfxData(data={"text": "hello"})
        # Should not raise type error
        result = process_data(wfx_data)
        assert result == "hello"

    def test_data_model_dump_compatible(self):
        """Test that model_dump works across module boundaries."""
        wfx_data = WfxData(data={"key": "value"})
        primeagent_data = PrimeagentData(**wfx_data.model_dump())
        assert primeagent_data.data == {"key": "value"}


class TestDuckTypingMessage:
    """Tests for duck-typing Message class across module boundaries."""

    def test_wfx_message_isinstance_primeagent_message(self):
        """Test that wfx.Message instance is recognized as primeagent.Message."""
        wfx_message = WfxMessage(text="hello")
        assert isinstance(wfx_message, PrimeagentMessage)

    def test_primeagent_message_isinstance_wfx_message(self):
        """Test that primeagent.Message instance is recognized as wfx.Message."""
        primeagent_message = PrimeagentMessage(text="hello")
        assert isinstance(primeagent_message, WfxMessage)

    def test_message_equality_across_modules(self):
        """Test that Message objects from different modules are equal."""
        wfx_message = WfxMessage(text="hello", sender="user")
        primeagent_message = PrimeagentMessage(text="hello", sender="user")
        # Note: Direct equality might not work due to timestamps
        assert wfx_message.text == primeagent_message.text
        assert wfx_message.sender == primeagent_message.sender

    def test_message_interchangeable_in_functions(self):
        """Test that Message from different modules work interchangeably."""

        def process_message(msg: PrimeagentMessage) -> str:
            return f"Processed: {msg.text}"

        wfx_message = WfxMessage(text="hello")
        # Should not raise type error
        result = process_message(wfx_message)
        assert result == "Processed: hello"

    def test_message_model_dump_compatible(self):
        """Test that model_dump works across module boundaries."""
        wfx_message = WfxMessage(text="hello", sender="user")
        dump = wfx_message.model_dump()
        primeagent_message = PrimeagentMessage(**dump)
        assert primeagent_message.text == "hello"
        assert primeagent_message.sender == "user"

    def test_message_inherits_data_duck_typing(self):
        """Test that Message inherits duck-typing from Data."""
        wfx_message = WfxMessage(text="hello")
        # Should work as Data too
        assert isinstance(wfx_message, PrimeagentData)
        assert isinstance(wfx_message, WfxData)


class TestContentBlockExcludeUnsetCrossModule:
    """primeagent and wfx ``ContentBlock`` copies must share the ``exclude_unset`` contract.

    Both ``__init__`` overrides mark only the ``type`` discriminator as set, so
    a partial patch like ``ContentBlock(title="...")`` dumps just the fields the
    caller touched. Marking every field set (the prior primeagent-base behavior)
    re-emitted defaulted ``duration`` / ``header`` / ``contents`` / ``media_url``
    and clobbered persisted values on the ``aupdate_messages`` merge.
    """

    def test_primeagent_content_block_exclude_unset_matches_wfx(self):
        from primeagent.schema.content_types import ContentBlock as PrimeagentContentBlock
        from wfx.schema.content_types import ContentBlock as WfxContentBlock

        primeagent_dump = PrimeagentContentBlock(title="new", allow_markdown=False).model_dump(exclude_unset=True)
        wfx_dump = WfxContentBlock(title="new", allow_markdown=False).model_dump(exclude_unset=True)

        assert primeagent_dump == wfx_dump
        assert primeagent_dump["type"] == "group"
        assert primeagent_dump.keys() <= {"type", "title", "allow_markdown"}


class TestDuckTypingWithInputs:
    """Tests for duck-typing with input validation."""

    def test_message_input_accepts_wfx_message(self):
        """Test that MessageInput accepts wfx.Message."""
        from wfx.inputs.inputs import MessageInput

        wfx_message = WfxMessage(text="hello")
        msg_input = MessageInput(name="test", value=wfx_message)
        assert isinstance(msg_input.value, (WfxMessage, PrimeagentMessage))

    def test_message_input_converts_cross_module(self):
        """Test that MessageInput handles cross-module Messages."""
        from wfx.inputs.inputs import MessageInput

        primeagent_message = PrimeagentMessage(text="hello")
        msg_input = MessageInput(name="test", value=primeagent_message)
        # Should recognize it as a Message
        assert msg_input.value.text == "hello"

    def test_data_input_accepts_wfx_data(self):
        """Test that DataInput accepts wfx.Data."""
        from wfx.inputs.inputs import DataInput

        wfx_data = WfxData(data={"key": "value"})
        data_input = DataInput(name="test", value=wfx_data)
        assert data_input.value == wfx_data


class TestDuckTypingEdgeCases:
    """Tests for edge cases in cross-module isinstance checks."""

    def test_different_class_name_not_cross_module(self):
        """Test that objects with different class names are not recognized as cross-module compatible."""
        from wfx.schema.cross_module import CrossModuleModel

        class CustomModel(CrossModuleModel):
            value: str

        custom = CustomModel(value="test")
        # Should not be considered a Data
        assert not isinstance(custom, WfxData)
        assert not isinstance(custom, PrimeagentData)

    def test_non_pydantic_model_not_cross_module(self):
        """Test that non-Pydantic objects are not recognized as cross-module compatible."""

        class FakeData:
            def __init__(self):
                self.data = {}

        fake = FakeData()
        assert not isinstance(fake, WfxData)
        assert not isinstance(fake, PrimeagentData)

    def test_missing_fields_not_cross_module(self):
        """Test that objects missing required fields are not recognized as cross-module compatible."""
        from wfx.schema.cross_module import CrossModuleModel

        class PartialData(CrossModuleModel):
            text_key: str

        partial = PartialData(text_key="text")
        # Should not be considered a full Data (missing data field)
        assert not isinstance(partial, WfxData)
        assert not isinstance(partial, PrimeagentData)


class TestDuckTypingInputMixin:
    """Tests for cross-module isinstance checks in BaseInputMixin and subclasses."""

    def test_base_input_mixin_is_cross_module(self):
        """Test that BaseInputMixin uses CrossModuleModel."""
        from wfx.inputs.input_mixin import BaseInputMixin
        from wfx.schema.cross_module import CrossModuleModel

        # Check that BaseInputMixin inherits from CrossModuleModel
        assert issubclass(BaseInputMixin, CrossModuleModel)

    def test_input_subclasses_inherit_cross_module(self):
        """Test that all input types inherit cross-module support."""
        from wfx.inputs.inputs import (
            BoolInput,
            DataInput,
            FloatInput,
            IntInput,
            MessageInput,
            StrInput,
        )
        from wfx.schema.cross_module import CrossModuleModel

        for input_class in [StrInput, IntInput, FloatInput, BoolInput, DataInput, MessageInput]:
            assert issubclass(input_class, CrossModuleModel)

    def test_input_instances_work_across_modules(self):
        """Test that input instances work with duck-typing."""
        from wfx.inputs.inputs import MessageInput

        # Create with wfx Message
        wfx_msg = WfxMessage(text="hello")
        input1 = MessageInput(name="test1", value=wfx_msg)

        # Create with primeagent Message
        primeagent_msg = PrimeagentMessage(text="world")
        input2 = MessageInput(name="test2", value=primeagent_msg)

        # Both should work
        assert input1.value.text == "hello"
        assert input2.value.text == "world"
