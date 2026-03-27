"""Ollama provider implementation.

Talks to a local Ollama instance via its HTTP API.
Supports both plain completion and structured output via JSON mode.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import aiohttp

from lens.providers.base import LLMResponse, ToolCall


@dataclass
class OllamaProvider:
    """LLM provider using a local Ollama instance.

    Args:
        model: Ollama model name (e.g., 'llama3.1', 'qwen2.5-coder:7b').
        base_url: Ollama API base URL.
    """

    model: str = "llama3.1"
    base_url: str = "http://localhost:11434"

    @property
    def model_name(self) -> str:
        return self.model

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

        return LLMResponse(
            text=data.get("response", ""),
            model=self.model,
            usage={
                "input_tokens": data.get("prompt_eval_count", 0),
                "output_tokens": data.get("eval_count", 0),
            },
        )

    async def complete_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        tool_choice: dict | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Simulate tool use by requesting JSON output from Ollama.

        Ollama doesn't natively support tool use, so we instruct the model
        to respond with JSON matching the tool's input schema.
        """
        # Build a JSON schema prompt from the first tool (or the chosen one)
        tool = tools[0]
        if tool_choice and tool_choice.get("name"):
            tool = next((t for t in tools if t["name"] == tool_choice["name"]), tools[0])

        schema = tool.get("input_schema", {})
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        schema_desc = "Respond with a JSON object containing these fields:\n"
        for prop_name, prop_info in properties.items():
            req = " (required)" if prop_name in required else ""
            schema_desc += f'  - "{prop_name}": {prop_info.get("description", prop_info.get("type", ""))}{req}\n'

        full_prompt = f"""{prompt}

{schema_desc}
Respond ONLY with valid JSON, no other text."""

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.3,  # Lower temp for structured output
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

        raw_text = data.get("response", "")

        # Parse JSON response into a tool call
        try:
            parsed = json.loads(raw_text)
            tool_calls = [ToolCall(name=tool["name"], arguments=parsed)]
        except json.JSONDecodeError:
            # Return raw text if JSON parsing fails
            return LLMResponse(text=raw_text, model=self.model)

        return LLMResponse(
            tool_calls=tool_calls,
            model=self.model,
            usage={
                "input_tokens": data.get("prompt_eval_count", 0),
                "output_tokens": data.get("eval_count", 0),
            },
        )
