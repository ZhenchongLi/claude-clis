"""Claude Code integration commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..shared.utils import CLIContext

console = Console()


def get_claude_dir() -> Path:
    """Get Claude Code configuration directory."""
    return Path.home() / ".claude"


def get_commands_dir() -> Path:
    """Get Claude Code commands directory."""
    claude_dir = get_claude_dir()
    return claude_dir / "commands"


def create_claude_command(
    name: str,
    description: str,
    command: str,
    working_dir: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Create a Claude Code command configuration."""
    return {
        "name": name,
        "description": description,
        "command": command,
        "working_directory": working_dir or ".",
        "tags": tags or [],
        "version": "1.0.0"
    }


@click.group(name="claude-code")
def claude_code_cmd() -> None:
    """🔧 Claude Code integration commands

    Register and manage claude-clis commands in Claude Code.
    """
    pass


@claude_code_cmd.command(name="register")
@click.option(
    "--name",
    default="claude-clis",
    help="Command name in Claude Code",
    show_default=True
)
@click.option(
    "--working-dir",
    default=None,
    help="Working directory for commands (defaults to current)"
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing commands"
)
@click.pass_obj
def register(ctx: CLIContext, name: str, working_dir: str | None, force: bool) -> None:
    """Register claude-clis commands to Claude Code.

    This creates Claude Code slash commands for all claude-clis tools,
    making them available directly in Claude Code sessions.
    """
    claude_dir = get_claude_dir()
    commands_dir = get_commands_dir()

    # Check if Claude Code is installed
    if not claude_dir.exists():
        ctx.error("Claude Code not found. Please install Claude Code first.")
        raise click.Abort()

    # Create commands directory if it doesn't exist
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Get current working directory
    current_dir = working_dir or str(Path.cwd())
    
    # Get absolute path to claude-clis executable
    import shutil
    claude_clis_path = shutil.which("claude-clis")
    if not claude_clis_path:
        ctx.error("claude-clis not found in PATH. Please ensure it's installed and accessible.")
        raise click.Abort()

    # Define commands to register
    commands_to_register = [
        {
            "filename": f"{name}-doc2md",
            "config": create_claude_command(
                name=f"/{name}-doc2md",
                description="Convert documents to Markdown using AI",
                command=f"{claude_clis_path} doc2md convert {{{{prompt}}}}",
                working_dir=current_dir,
                tags=["document", "conversion", "ai", "markdown"]
            )
        },
        {
            "filename": f"{name}-doc2md-batch",
            "config": create_claude_command(
                name=f"/{name}-doc2md-batch",
                description="Batch convert documents to Markdown",
                command=f"{claude_clis_path} doc2md batch {{{{prompt}}}}",
                working_dir=current_dir,
                tags=["document", "conversion", "ai", "batch"]
            )
        },
        {
            "filename": f"{name}-config",
            "config": create_claude_command(
                name=f"/{name}-config",
                description="Manage claude-clis configuration",
                command=f"{claude_clis_path} config {{{{prompt}}}}",
                working_dir=current_dir,
                tags=["configuration", "setup"]
            )
        },
        {
            "filename": f"{name}-help",
            "config": create_claude_command(
                name=f"/{name}-help",
                description="Show claude-clis help and available commands",
                command=f"{claude_clis_path} --help",
                working_dir=current_dir,
                tags=["help", "documentation"]
            )
        }
    ]

    registered_commands = []
    skipped_commands = []

    for cmd_info in commands_to_register:
        cmd_file = commands_dir / f"{cmd_info['filename']}.json"

        if cmd_file.exists() and not force:
            skipped_commands.append(cmd_info['config']['name'])
            continue

        try:
            with open(cmd_file, 'w', encoding='utf-8') as f:
                json.dump(cmd_info['config'], f, indent=2)

            registered_commands.append(cmd_info['config']['name'])

        except Exception as e:
            ctx.error(f"Failed to register {cmd_info['config']['name']}: {e}")

    # Show results
    if registered_commands:
        table = Table(title="✅ Registered Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")

        for cmd_info in commands_to_register:
            cmd_name = cmd_info['config']['name']
            if cmd_name in registered_commands:
                table.add_row(
                    cmd_name,
                    cmd_info['config']['description']
                )

        console.print(table)
        console.print()

    if skipped_commands:
        console.print(
            Panel(
                f"⚠️  Skipped existing commands: {', '.join(skipped_commands)}\n"
                f"Use --force to overwrite existing commands",
                title="Skipped",
                border_style="yellow"
            )
        )
        console.print()

    console.print(
        Panel(
            "🎉 Commands registered successfully!\n\n"
            "You can now use these commands in Claude Code:\n"
            f"• {name}-doc2md <file.pdf>\n"
            f"• {name}-doc2md-batch <directory>\n"
            f"• {name}-config show\n"
            f"• {name}-help\n\n"
            f"📁 Commands saved to: {commands_dir}",
            title="Registration Complete",
            border_style="green"
        )
    )


@claude_code_cmd.command(name="unregister")
@click.option(
    "--name",
    default="claude-clis",
    help="Command name prefix to unregister",
    show_default=True
)
@click.option(
    "--all",
    "unregister_all",
    is_flag=True,
    help="Unregister all claude-clis commands"
)
@click.pass_obj
def unregister(ctx: CLIContext, name: str, unregister_all: bool) -> None:
    """Unregister claude-clis commands from Claude Code."""
    commands_dir = get_commands_dir()

    if not commands_dir.exists():
        ctx.warning("No Claude Code commands directory found.")
        return

    # Find commands to remove
    pattern = f"{name}-*" if not unregister_all else "claude-clis-*"
    command_files = list(commands_dir.glob(f"{pattern}.json"))

    if not command_files:
        ctx.warning(f"No commands found matching pattern: {pattern}")
        return

    removed_commands = []
    for cmd_file in command_files:
        try:
            # Read command info for display
            with open(cmd_file, 'r', encoding='utf-8') as f:
                cmd_config = json.load(f)

            cmd_file.unlink()
            removed_commands.append(cmd_config.get('name', cmd_file.stem))

        except Exception as e:
            ctx.error(f"Failed to remove {cmd_file.name}: {e}")

    if removed_commands:
        console.print(
            Panel(
                f"🗑️  Removed commands:\n" + "\n".join(f"• {cmd}" for cmd in removed_commands),
                title="Unregistration Complete",
                border_style="red"
            )
        )
    else:
        ctx.warning("No commands were removed.")


@claude_code_cmd.command(name="list")
@click.option(
    "--name",
    default="claude-clis",
    help="Filter by command name prefix",
    show_default=True
)
@click.pass_obj
def list_commands(ctx: CLIContext, name: str) -> None:
    """List registered claude-clis commands in Claude Code."""
    commands_dir = get_commands_dir()

    if not commands_dir.exists():
        ctx.warning("No Claude Code commands directory found.")
        return

    # Find matching commands
    command_files = list(commands_dir.glob(f"{name}-*.json"))

    if not command_files:
        ctx.warning(f"No commands found with prefix: {name}")
        return

    table = Table(title=f"📋 Registered Commands ({name})")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Tags", style="dim")

    for cmd_file in sorted(command_files):
        try:
            with open(cmd_file, 'r', encoding='utf-8') as f:
                cmd_config = json.load(f)

            table.add_row(
                cmd_config.get('name', 'N/A'),
                cmd_config.get('description', 'N/A'),
                ', '.join(cmd_config.get('tags', []))
            )

        except Exception as e:
            ctx.error(f"Error reading {cmd_file.name}: {e}")

    console.print(table)


@claude_code_cmd.command(name="status")
@click.pass_obj
def status(cli_ctx: CLIContext) -> None:
    """Show Claude Code integration status."""
    claude_dir = get_claude_dir()
    commands_dir = get_commands_dir()

    # Check Claude Code installation
    claude_installed = claude_dir.exists()

    # Count registered commands
    registered_count = 0
    if commands_dir.exists():
        registered_count = len(list(commands_dir.glob("claude-clis-*.json")))

    # Create status table
    table = Table(title="🔧 Claude Code Integration Status")
    table.add_column("Item", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    table.add_row(
        "Claude Code",
        "✅ Installed" if claude_installed else "❌ Not Found",
        str(claude_dir) if claude_installed else "Install Claude Code first"
    )

    table.add_row(
        "Commands Directory",
        "✅ Available" if commands_dir.exists() else "⚠️  Not Created",
        str(commands_dir)
    )

    table.add_row(
        "Registered Commands",
        f"📊 {registered_count} commands",
        "Use 'list' command to see details"
    )

    console.print(table)

    if claude_installed and registered_count == 0:
        console.print()
        console.print(
            Panel(
                "💡 No commands registered yet!\n\n"
                "Run: claude-clis claude-code register\n"
                "to register all claude-clis commands in Claude Code.",
                title="Quick Start",
                border_style="blue"
            )
        )