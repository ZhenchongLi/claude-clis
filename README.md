# Claude CLI Tools

A modern collection of AI-powered CLI tools for document processing, content generation, and more. Built with Python 3.11+, powered by multiple AI providers (Gemini, Ollama, Anthropic Claude).

## Features

- **Multi-AI Provider Support**: Switch seamlessly between Gemini, Ollama, and Anthropic Claude
- **Document Conversion**: Convert PDF and DOCX files to clean, structured Markdown
- **Modern Python**: Built with Python 3.11+, type hints, and modern best practices
- **Easy Configuration**: Simple YAML-based configuration with environment variable support
- **Type Safe**: Full type annotations with mypy validation
- **uv Package Management**: Fast, reliable dependency management with uv

## Available Tools

### doc2md - Document to Markdown Converter

Convert PDF and DOCX documents to clean, AI-processed Markdown:

```bash
# Convert a single document
claude-clis doc2md convert document.pdf -o output.md

# Batch convert all documents in a directory
claude-clis doc2md batch /path/to/docs/ --output-dir ./markdown/

# Use specific AI provider
claude-clis doc2md convert document.pdf --ai-provider ollama

# Different output styles
claude-clis doc2md convert document.pdf --style academic
```

**Supported formats:** PDF, DOCX, DOC, TXT, MD

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv package manager](https://github.com/astral-sh/uv) (recommended)

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/claude-clis.git
cd claude-clis

# Install in development mode
uv pip install -e .

# Or install from PyPI (when published)
uv add claude-clis
```

### Install with pip

```bash
pip install claude-clis
```

## Quick Start

### 1. Initialize Configuration

```bash
# Set up configuration with guided setup
claude-clis config init

# Or manually configure your preferred AI provider
claude-clis config set ai.provider gemini
claude-clis config set ai.gemini.api_key YOUR_API_KEY
```

### 2. Convert Your First Document

```bash
# Convert a PDF to Markdown
claude-clis doc2md convert document.pdf

# View document info before conversion
claude-clis doc2md info document.pdf

# Test your setup
claude-clis doc2md test
```

### 3. Explore Available Tools

```bash
# List all available tools
claude-clis list

# Get help for any command
claude-clis doc2md --help
claude-clis config --help
```

## Configuration

Claude CLI Tools uses a YAML configuration file located at `~/.claude-clis/config.yaml`.

### AI Provider Setup

#### Gemini (Recommended - Free tier available)

```bash
claude-clis config set ai.provider gemini
claude-clis config set ai.gemini.api_key YOUR_GEMINI_API_KEY
```

Get your API key at: [Google AI Studio](https://makersuite.google.com/app/apikey)

#### Ollama (Local/Privacy-focused)

```bash
# Install and start Ollama
ollama serve
ollama pull llama3.2

# Configure Claude CLI Tools
claude-clis config set ai.provider ollama
claude-clis config set ai.ollama.model llama3.2:latest
```

#### Anthropic Claude

```bash
claude-clis config set ai.provider anthropic
claude-clis config set ai.anthropic.api_key YOUR_CLAUDE_API_KEY
```

Get your API key at: [Anthropic Console](https://console.anthropic.com/)

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/your-username/claude-clis.git
cd claude-clis

# Install dependencies
uv pip install -e .

# Install development dependencies
uv add --dev pytest mypy black ruff pytest-cov
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=claude_clis

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
uv run black src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Made with Claude Code

This project was generated using Claude Code, Anthropic's official CLI for Claude.