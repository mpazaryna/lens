---
name: Ollama-first development
description: First dev pass for enrichment pipeline uses local Ollama, not cloud APIs
type: project
---

First dev pass of enrichment pipeline uses only local Ollama instance (http://localhost:11434). No cloud API calls during initial development. Available models include llama3.2, qwen2.5-coder:7b, devstral:24b, llama3.2-vision:11b.

**Why:** Privacy, cost control, and no API key dependency during development.

**How to apply:** When implementing enrichment steps, configure provider as ollama with a local model. Integration tests should target Ollama. Cloud providers are for production config only.
