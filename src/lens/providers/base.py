"""Provider protocol: the interface all LLM providers implement."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class ToolCall:
    """A tool/function call returned by the model."""

    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class LLMResponse:
    """Unified response from any LLM provider."""

    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol that all LLM providers must implement."""

    @property
    def model_name(self) -> str:
        """The model identifier this provider is configured to use."""
        ...

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send a prompt and get a text completion.

        Args:
            prompt: The user message.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature.

        Returns:
            LLMResponse with text content.
        """
        ...

    async def complete_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        tool_choice: dict | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Send a prompt with tool definitions and get structured output.

        Args:
            prompt: The user message.
            tools: Tool definitions in Anthropic-style format.
            tool_choice: Optional tool choice constraint.
            max_tokens: Maximum tokens in the response.

        Returns:
            LLMResponse with tool_calls populated.
        """
        ...
