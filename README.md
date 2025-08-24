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

### Install with pipx (Recommended)

[pipx](https://pipx.pypa.io/) is the best way to install CLI tools like claude-clis. It creates an isolated environment for each tool while making the commands globally available.

```bash
# Install pipx if you haven't already
pip install pipx
pipx ensurepath

# Install claude-clis from PyPI (when published)
pipx install claude-clis

# Or install directly from GitHub
pipx install git+https://github.com/your-username/claude-clis.git

# Upgrade to latest version
pipx upgrade claude-clis

# Uninstall cleanly
pipx uninstall claude-clis
```

### Alternative Installation Methods

#### Install with uv

```bash
# Clone the repository
git clone https://github.com/your-username/claude-clis.git
cd claude-clis

# Install in development mode
uv pip install -e .

# Or install from PyPI (when published)
uv add claude-clis
```

#### Install with pip

```bash
# From PyPI (when published)
pip install claude-clis

# Or from source
pip install git+https://github.com/your-username/claude-clis.git
```

### Installation Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **pipx** | End users | Isolated environment, global commands | Requires pipx installation |
| **uv** | Developers | Fast, modern package management | Newer tool |
| **pip** | Traditional setup | Widely available | May cause dependency conflicts |

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

## Claude Code Integration

Integrate claude-clis commands directly into Claude Code sessions for seamless usage.

### Register Commands

```bash
# Register all claude-clis commands to Claude Code
claude-clis claude-code register

# Use custom command names
claude-clis claude-code register --name my-tools

# Force override existing commands
claude-clis claude-code register --force
```

### Manage Registered Commands

```bash
# List registered commands
claude-clis claude-code list

# Check integration status
claude-clis claude-code status

# Unregister commands
claude-clis claude-code unregister

# Unregister all commands
claude-clis claude-code unregister --all
```

### Usage in Claude Code

After registration, use these slash commands in Claude Code:

```
/claude-clis-doc2md document.pdf
/claude-clis-doc2md-batch /path/to/docs/
/claude-clis-config show
/claude-clis-help
```

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