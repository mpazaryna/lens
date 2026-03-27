"""Anthropic provider implementation."""

from __future__ import annotations

from dataclasses import dataclass

import anthropic

from lens.providers.base import LLMResponse, ToolCall


@dataclass
class AnthropicProvider:
    """LLM provider using the Anthropic API."""

    api_key: str
    model: str = "claude-sonnet-4-20250514"

    @property
    def model_name(self) -> str:
        return self.model

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        client = anthropic.AsyncAnthropic(api_key=self.api_key)
        message = await client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        text = message.content[0].text if message.content else None
        usage = {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }

        return LLMResponse(text=text, model=self.model, usage=usage)

    async def complete_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        tool_choice: dict | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "tools": tools,
            "messages": [{"role": "user", "content": prompt}],
        }
        if tool_choice:
            kwargs["tool_choice"] = tool_choice

        message = await client.messages.create(**kwargs)

        tool_calls = []
        text = None
        for block in message.content:
            if block.type == "tool_use":
                tool_calls.append(ToolCall(name=block.name, arguments=block.input))
            elif block.type == "text":
                text = block.text

        usage = {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }

        return LLMResponse(text=text, tool_calls=tool_calls, model=self.model, usage=usage)
