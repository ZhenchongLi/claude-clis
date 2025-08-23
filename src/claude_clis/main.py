from __future__ import annotations

import sys
from typing import Any

import click
import rich_click as rich_click
from rich.console import Console
from rich.table import Table

from .shared.config import config_manager
from .shared.utils import CLIContext, print_error, print_info, print_success, print_table

# Configure rich-click
rich_click.rich_click.USE_RICH_MARKUP = True
rich_click.rich_click.USE_MARKDOWN = True
rich_click.rich_click.SHOW_ARGUMENTS = True
rich_click.rich_click.GROUP_ARGUMENTS_OPTIONS = True


console = Console()


@click.group(
    name="claude-clis",
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True
)
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose output"
)
@click.option(
    "--quiet", "-q", 
    is_flag=True, 
    help="Suppress all output except errors"
)
@click.pass_context
def main(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """🤖 **Claude CLI Tools** - A collection of AI-powered CLI tools
    
    A modern toolkit for document processing, content generation, and more,
    powered by multiple AI providers (Gemini, Ollama, Anthropic Claude).
    
    **Available Tools:**
    - `doc2md`: Convert documents (PDF, DOCX) to Markdown using AI
    
    **Quick Start:**
    ```bash
    # Set up your AI provider
    claude-clis config set ai.provider gemini
    claude-clis config set ai.gemini.api_key YOUR_API_KEY
    
    # Convert a document
    claude-clis doc2md convert document.pdf -o output.md
    ```
    
    Use `claude-clis COMMAND --help` for detailed help on any command.
    """
    # Create CLI context
    cli_ctx = CLIContext()
    cli_ctx.verbose = verbose
    cli_ctx.quiet = quiet
    ctx.obj = cli_ctx
    
    # If no command is provided, show available tools
    if ctx.invoked_subcommand is None:
        show_tools_list(cli_ctx)


@main.command()
@click.pass_obj
def list(cli_ctx: CLIContext) -> None:
    """📋 List all available tools and their descriptions"""
    show_tools_list(cli_ctx)


@main.group()
@click.pass_context
def config(ctx: click.Context) -> None:
    """⚙️ Configuration management
    
    Manage global configuration for Claude CLI Tools, including AI provider
    settings, API keys, and tool-specific preferences.
    
    **Examples:**
    ```bash
    # Set AI provider
    claude-clis config set ai.provider gemini
    
    # Set API key
    claude-clis config set ai.gemini.api_key YOUR_KEY
    
    # Show current configuration
    claude-clis config show
    ```
    """
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_obj
def config_set(cli_ctx: CLIContext, key: str, value: str) -> None:
    """✏️ Set a configuration value
    
    **KEY**: Configuration key (e.g., 'ai.provider', 'ai.gemini.api_key')
    **VALUE**: Value to set
    """
    try:
        config_manager.set_config_value(key, value)
        cli_ctx.success(f"Set {key} = {value}")
    except Exception as e:
        cli_ctx.error(f"Failed to set config: {str(e)}")
        sys.exit(1)


@config.command("get")
@click.argument("key")
@click.pass_obj
def config_get(cli_ctx: CLIContext, key: str) -> None:
    """📖 Get a configuration value
    
    **KEY**: Configuration key to retrieve
    """
    try:
        value = config_manager.get_config_value(key)
        print(value)
    except Exception as e:
        cli_ctx.error(f"Failed to get config: {str(e)}")
        sys.exit(1)


@config.command("show")
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "yaml"]),
    default="table",
    help="Output format"
)
@click.pass_obj
def config_show(cli_ctx: CLIContext, format: str) -> None:
    """👀 Show current configuration"""
    try:
        config_dict = config_manager.show_config()
        
        if format == "yaml":
            import yaml
            print(yaml.dump(config_dict, default_flow_style=False, indent=2))
        else:
            _print_config_table(config_dict)
    except Exception as e:
        cli_ctx.error(f"Failed to show config: {str(e)}")
        sys.exit(1)


@config.command("init")
@click.option(
    "--provider",
    type=click.Choice(["gemini", "ollama", "anthropic"]),
    default="gemini",
    help="Default AI provider"
)
@click.pass_obj
def config_init(cli_ctx: CLIContext, provider: str) -> None:
    """🚀 Initialize configuration with guided setup"""
    cli_ctx.info("🔧 Setting up Claude CLI Tools configuration...")
    
    try:
        # Ensure config directory exists
        config_manager.ensure_config_dir()
        
        # Set provider
        config_manager.set_config_value("ai.provider", provider)
        cli_ctx.success(f"Set AI provider to: {provider}")
        
        # Provider-specific setup
        if provider == "gemini":
            cli_ctx.info("📝 Please set your Gemini API key:")
            cli_ctx.info("   claude-clis config set ai.gemini.api_key YOUR_API_KEY")
            cli_ctx.info("   Get your key at: https://makersuite.google.com/app/apikey")
        elif provider == "anthropic":
            cli_ctx.info("📝 Please set your Anthropic API key:")
            cli_ctx.info("   claude-clis config set ai.anthropic.api_key YOUR_API_KEY")
            cli_ctx.info("   Get your key at: https://console.anthropic.com/")
        elif provider == "ollama":
            cli_ctx.info("📝 Make sure Ollama is running locally:")
            cli_ctx.info("   Install: https://ollama.ai/")
            cli_ctx.info("   Run: ollama serve")
            cli_ctx.info("   Pull a model: ollama pull llama3.2")
        
        cli_ctx.success("✅ Configuration initialized!")
        cli_ctx.info(f"📁 Config location: {config_manager.config_file}")
        
    except Exception as e:
        cli_ctx.error(f"Failed to initialize config: {str(e)}")
        sys.exit(1)


def show_tools_list(cli_ctx: CLIContext) -> None:
    """Display available tools in a formatted table"""
    tools = [
        ["doc2md", "Convert documents to Markdown", "PDF, DOCX → Markdown"],
        ["config", "Manage configuration", "AI providers, API keys"],
    ]
    
    cli_ctx.info("🤖 Claude CLI Tools - Available Tools:")
    print_table(
        "",
        ["Tool", "Description", "Formats"],
        tools,
        show_header=True
    )
    
    cli_ctx.info("\n💡 Quick Start:")
    cli_ctx.info("  1. claude-clis config init")
    cli_ctx.info("  2. claude-clis doc2md convert file.pdf")
    cli_ctx.info("\n📖 Use --help with any command for detailed information")


def _print_config_table(config_dict: dict[str, Any], prefix: str = "") -> None:
    """Print configuration as a formatted table"""
    rows = []
    
    def flatten_dict(d: dict[str, Any], parent_key: str = "") -> None:
        for key, value in d.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                flatten_dict(value, full_key)
            else:
                # Hide sensitive values
                display_value = "***" if "key" in key.lower() and value else str(value)
                rows.append([full_key, display_value])
    
    flatten_dict(config_dict)
    
    print_table(
        "Current Configuration",
        ["Key", "Value"],
        rows,
        show_header=True
    )


# Register tools
def register_tools() -> None:
    """Register all available tools with the main CLI"""
    try:
        from .tools.doc2md.cli import doc2md
        main.add_command(doc2md)
    except ImportError as e:
        # Handle gracefully if optional tools are not available
        print_error(f"Failed to load doc2md tool: {e}")


# Register tools when module is imported
register_tools()


if __name__ == "__main__":
    main()