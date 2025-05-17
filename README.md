# Lens: Content-Aware Feed Aggregator

## Overview

Lens is a next-generation feed aggregator that uses local AI models to intelligently filter, rank, and recommend content from RSS feeds based on user interests. The system distinguishes between different content types (particularly video vs. article content) and uses specialized processing paths for each, learning user preferences for topics and content formats over time.

## Key Features

- **Content-Type Awareness**: Specialized processing for videos and articles
- **Local AI Processing**: Uses Ollama for privacy-preserving content analysis
- **Natural Language Queries**: Ask for content in plain English
- **Personalized Recommendations**: Learns your preferences over time
- **Command-Line Interface**: Fast, efficient content discovery
- **Functional Programming**: Built with functional programming principles for clarity and maintainability

## Getting Started

### Prerequisites

- [Deno](https://deno.land/) runtime
- [Ollama](https://ollama.ai/) for local AI models
- Recommended models:
  - An embedding model (e.g., nomic-embed-text)
  - A general-purpose LLM (e.g., llama2 or mistral)

### Installation

```bash
# Clone the repository
git clone https://github.com/mpazaryna/lens.git
cd lens

# Update environment variables in .env file
cp .env.example .env

# Run the tests
deno task test
```

## Architecture

Lens uses a modular architecture with specialized processing paths for different content types:

```mermaid
flowchart TD
    A[RSS Source Registry] --> B[Retrieval Engine]
    B --> C[Video Content Path]
    B --> D[Article Content Path]
    C --> E[Video Processor]
    D --> F[Article Processor]
    E --> G[Video Embeddings]
    F --> H[Article Embeddings]
    G --> I[Vector Database]
    H --> I
    I --> J[Query Engine]
    J --> K[User Interface]
```

## Development Status

Lens is currently in active development. See the [project roadmap](docs/prd/roadmap.md) for more details on upcoming features and milestones.

## Contributing

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Deno](https://deno.land/)
- AI capabilities powered by [Ollama](https://ollama.ai/)
- Inspired by traditional RSS readers and modern AI assistants