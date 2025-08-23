from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import rich.console
import rich.progress
import rich.table
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table


console = Console()


def print_info(message: str) -> None:
    console.print(f"[blue]ℹ[/blue] {message}")


def print_success(message: str) -> None:
    console.print(f"[green]✅[/green] {message}")


def print_warning(message: str) -> None:
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_error(message: str) -> None:
    console.print(f"[red]❌[/red] {message}")


def print_panel(title: str, content: str, style: str = "blue") -> None:
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)


def print_code(code: str, language: str = "python") -> None:
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def confirm_action(message: str, default: bool = False) -> bool:
    return Confirm.ask(message, default=default)


def prompt_input(message: str, default: str = "") -> str:
    return Prompt.ask(message, default=default)


def create_progress_bar(description: str = "Processing...") -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip('. ')
    return filename[:255] if len(filename) > 255 else filename


def ensure_directory(path: Path | str) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(file_path: Path | str) -> str:
    return Path(file_path).suffix.lower()


def is_supported_document(file_path: Path | str) -> bool:
    supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    return get_file_extension(file_path) in supported_extensions


def find_files(
    directory: Path | str, 
    patterns: list[str] | None = None, 
    recursive: bool = True
) -> list[Path]:
    directory = Path(directory)
    
    if not directory.exists():
        return []
    
    files = []
    glob_pattern = "**/*" if recursive else "*"
    
    for file_path in directory.glob(glob_pattern):
        if file_path.is_file():
            if patterns:
                if any(file_path.match(pattern) for pattern in patterns):
                    files.append(file_path)
            else:
                files.append(file_path)
    
    return sorted(files)


def create_table(
    title: str,
    columns: list[str],
    rows: list[list[str]],
    show_header: bool = True,
) -> Table:
    table = Table(title=title, show_header=show_header)
    
    for column in columns:
        table.add_column(column)
    
    for row in rows:
        table.add_row(*row)
    
    return table


def print_table(
    title: str,
    columns: list[str],
    rows: list[list[str]],
    show_header: bool = True,
) -> None:
    table = create_table(title, columns, rows, show_header)
    console.print(table)


class FileProcessor:
    @staticmethod
    def read_text_file(file_path: Path | str, encoding: str = "utf-8") -> str:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try alternative encodings
            encodings = ["utf-8-sig", "latin-1", "cp1252"]
            for enc in encodings:
                try:
                    with open(file_path, "r", encoding=enc) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Could not decode file {file_path} with any supported encoding")

    @staticmethod
    def write_text_file(
        file_path: Path | str, 
        content: str, 
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> None:
        file_path = Path(file_path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)

    @staticmethod
    def backup_file(file_path: Path | str, suffix: str = ".bak") -> Path:
        file_path = Path(file_path)
        backup_path = file_path.with_suffix(file_path.suffix + suffix)
        
        counter = 1
        while backup_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}{suffix}.{counter}")
            counter += 1
        
        if file_path.exists():
            file_path.rename(backup_path)
            return backup_path
        
        raise FileNotFoundError(f"File {file_path} does not exist")


def validate_output_path(output_path: str | None, input_path: str, default_extension: str = ".md") -> Path:
    if output_path:
        return Path(output_path)
    
    input_path_obj = Path(input_path)
    return input_path_obj.with_suffix(default_extension)


def get_relative_path(file_path: Path | str, base_path: Path | str | None = None) -> str:
    file_path = Path(file_path)
    base_path = Path(base_path) if base_path else Path.cwd()
    
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)


def format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


class CLIContext:
    def __init__(self) -> None:
        self.verbose: bool = False
        self.quiet: bool = False
        self.dry_run: bool = False

    def log(self, message: str, level: str = "info") -> None:
        if self.quiet:
            return
        
        if level == "debug" and not self.verbose:
            return
        
        if level == "info":
            print_info(message)
        elif level == "success":
            print_success(message)
        elif level == "warning":
            print_warning(message)
        elif level == "error":
            print_error(message)
        elif level == "debug" and self.verbose:
            console.print(f"[dim]🔍 {message}[/dim]")

    def debug(self, message: str) -> None:
        self.log(message, "debug")

    def info(self, message: str) -> None:
        self.log(message, "info")

    def success(self, message: str) -> None:
        self.log(message, "success")

    def warning(self, message: str) -> None:
        self.log(message, "warning")

    def error(self, message: str) -> None:
        self.log(message, "error")