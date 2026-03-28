"""OpenAI provider implementation.

Supports OpenAI API and any compatible endpoint (Azure, Together, etc.)
by setting a custom base_url.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from lens.providers.base import LLMResponse, ToolCall


def _anthropic_tool_to_openai(tool: dict) -> dict:
    """Convert Anthropic-style tool definition to OpenAI function format."""
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool.get("input_schema", {}),
        },
    }


@dataclass
class OpenAIProvider:
    """LLM provider using the OpenAI API.

    Also works with any OpenAI-compatible endpoint (Azure, Together, Groq, etc.)
    by setting base_url.
    """

    api_key: str
    model: str = "gpt-4o"
    base_url: str | None = None

    @property
    def model_name(self) -> str:
        return self.model

    def _get_client(self):
        import openai

        kwargs: dict = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return openai.AsyncOpenAI(**kwargs)

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        choice = response.choices[0]
        text = choice.message.content
        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }

        return LLMResponse(text=text, model=self.model, usage=usage)

    async def complete_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        tool_choice: dict | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        client = self._get_client()

        openai_tools = [_anthropic_tool_to_openai(t) for t in tools]

        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "tools": openai_tools,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Convert Anthropic tool_choice to OpenAI format
        if tool_choice and tool_choice.get("type") == "tool":
            kwargs["tool_choice"] = {
                "type": "function",
                "function": {"name": tool_choice["name"]},
            }

        response = await client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        text = choice.message.content
        tool_calls = []

        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }

        return LLMResponse(text=text, tool_calls=tool_calls, model=self.model, usage=usage)
