# Contributing to Lens

Thank you for your interest in contributing to Lens! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Contributing to Lens](#contributing-to-lens)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [Getting Started](#getting-started)
  - [Development Workflow](#development-workflow)
  - [Testing Requirements](#testing-requirements)
  - [Pull Request Process](#pull-request-process)
  - [Coding Standards](#coding-standards)
  - [Documentation](#documentation)
  - [Community](#community)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. Please be kind and constructive in your communications.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/lens.git
   cd lens
   ```
3. **Set up the development environment**:
   ```bash
   # Install Deno if you haven't already
   # https://deno.land/#installation

   # Install Ollama if you haven't already
   # https://ollama.ai/download

   # Run the setup script
   deno run --allow-all setup.ts
   ```

## Development Workflow

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them with clear, descriptive commit messages:
   ```bash
   git commit -m "Add feature: description of the changes"
   ```

3. **Write or update tests** for your changes (see [Testing Requirements](#testing-requirements))

4. **Run tests** to ensure they pass:
   ```bash
   deno test
   ```

5. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a pull request** to the main repository

## Testing Requirements

**All contributions require valid and passing tests.** This is a critical requirement for all pull requests.

- Write tests for all new features and bug fixes
- Update existing tests when modifying functionality
- Ensure all tests pass before submitting your pull request
- Include both unit tests and integration tests where appropriate
- Test coverage should be maintained or improved with each contribution

To run the test suite:

```bash
# Run all tests
deno test

# Run tests with coverage
deno test --coverage

# Run specific tests
deno test path/to/test_file.ts
```

## Pull Request Process

1. Ensure your code follows the project's coding standards
2. Update documentation as needed
3. Include a clear description of the changes in your pull request
4. Link any related issues in your pull request description
5. All tests must pass before a pull request can be merged
6. Code review approval is required before merging
7. Maintainers may request changes or improvements before merging

## Coding Standards

### Labs and Experimental Code

Labs are a part of the folder structure where experimental features, proof-of-concept implementations, and features in incubation are developed. When working with experimental code:

- Label experimental features clearly
- Document the purpose and status of experimental code
- Include appropriate tests for experimental features
- Consider the path to integration with the main codebase

For more details on our labs approach, see our [Labs Approach Guide](./docs/devlog/DEV-005-labs.md).

### Programming Paradigm

Lens uses functional programming principles rather than object-oriented programming. When contributing code:

- Write pure functions whenever possible
- Treat data as immutable
- Compose complex operations from simpler functions
- Minimize and make state changes explicit
- Avoid classes with internal state, inheritance, and methods that modify object state

For detailed examples and explanations, see our [Functional Programming Guide](./docs/devlog/DEV-002-functional-programming.md).

### General Standards

- Follow the TypeScript best practices
- Use consistent formatting (the project uses Deno's built-in formatter)
- Run `deno fmt` before committing to ensure consistent formatting
- Follow the existing code structure and patterns
- Use meaningful variable and function names
- Include comments for complex logic

## Documentation

- Update README.md if you change functionality
- Document all public APIs, functions, and components
- Include examples in documentation where helpful
- Keep documentation up-to-date with code changes

## Community

- Join our community discussions
- Help answer questions from other contributors
- Provide feedback on issues and pull requests
- Share your experience using Lens

Thank you for contributing to Lens!
