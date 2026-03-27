"""Tests for provider base types."""

import pytest

from lens.providers.base import LLMResponse, ToolCall


class TestToolCall:
    """Tests for ToolCall dataclass."""

    def test_frozen(self) -> None:
        tc = ToolCall(name="test", arguments={"key": "value"})
        with pytest.raises(AttributeError):
            tc.name = "modified"  # type: ignore[misc]

    def test_stores_arguments(self) -> None:
        tc = ToolCall(name="fn", arguments={"score": 8.5, "tags": ["a", "b"]})
        assert tc.arguments["score"] == 8.5
        assert tc.arguments["tags"] == ["a", "b"]


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_text_response(self) -> None:
        resp = LLMResponse(text="Hello", model="test")
        assert resp.text == "Hello"
        assert resp.tool_calls == []

    def test_tool_call_response(self) -> None:
        tc = ToolCall(name="score", arguments={"score": 9})
        resp = LLMResponse(tool_calls=[tc], model="test")
        assert resp.text is None
        assert len(resp.tool_calls) == 1
        assert resp.tool_calls[0].name == "score"

    def test_frozen(self) -> None:
        resp = LLMResponse(text="test", model="m")
        with pytest.raises(AttributeError):
            resp.text = "modified"  # type: ignore[misc]

    def test_defaults(self) -> None:
        resp = LLMResponse()
        assert resp.text is None
        assert resp.tool_calls == []
        assert resp.model == ""
        assert resp.usage == {}
