from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click

from ...shared.config import config_manager
from ...shared.utils import CLIContext
from .processor import Doc2mdProcessor, ProcessorError


@click.group(name="doc2md")
@click.pass_context
def doc2md(ctx: click.Context) -> None:
    """📄 Document to Markdown converter
    
    Convert PDF and DOCX documents to clean, well-structured Markdown using AI.
    
    **Supported formats:**
    - PDF (.pdf)
    - Microsoft Word (.docx, .doc)  
    - Plain text (.txt)
    - Markdown (.md)
    
    **Examples:**
    ```bash
    # Convert single document
    claude-clis doc2md convert document.pdf
    
    # Convert with custom output
    claude-clis doc2md convert document.pdf -o output.md
    
    # Use specific AI provider
    claude-clis doc2md convert document.pdf --ai-provider ollama
    
    # Batch convert directory
    claude-clis doc2md batch /path/to/docs/ --output-dir ./markdown/
    ```
    """
    pass


@doc2md.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output", "output_file",
    type=click.Path(path_type=Path),
    help="Output file path (default: input_file.md)"
)
@click.option(
    "--ai-provider",
    type=click.Choice(["gemini", "ollama", "anthropic"]),
    help="AI provider to use (overrides config)"
)
@click.option(
    "--style",
    type=click.Choice(["technical", "academic", "business", "casual"]),
    default="technical",
    help="Output style"
)
@click.option(
    "--sections",
    type=click.Choice(["auto", "preserve", "flatten"]),
    default="auto",
    help="Section handling strategy"
)
@click.option(
    "--chunk-size",
    type=int,
    default=4000,
    help="Text chunk size for processing"
)
@click.option(
    "--no-formatting",
    is_flag=True,
    help="Don't preserve original formatting"
)
@click.pass_obj
def convert(
    cli_ctx: CLIContext,
    input_file: Path,
    output_file: Path | None,
    ai_provider: str | None,
    style: str,
    sections: str,
    chunk_size: int,
    no_formatting: bool,
) -> None:
    """🔄 Convert a single document to Markdown
    
    **INPUT_FILE**: Path to the document to convert
    
    The tool will automatically detect the file format and use the appropriate
    reader to extract content, then convert it to clean Markdown using AI.
    """
    try:
        processor = Doc2mdProcessor(cli_ctx)
        
        # Check if file format is supported
        if not processor.is_supported_format(input_file):
            supported = ", ".join(processor.get_supported_formats())
            cli_ctx.error(f"Unsupported file format. Supported: {supported}")
            sys.exit(1)
        
        # Validate AI provider
        if ai_provider:
            if not processor.ai_client.test_provider(ai_provider):
                cli_ctx.error(f"AI provider '{ai_provider}' is not properly configured")
                cli_ctx.info("Run: claude-clis config init")
                sys.exit(1)
        
        # Run conversion
        result_path = asyncio.run(processor.convert_file(
            input_file=input_file,
            output_file=output_file,
            ai_provider=ai_provider,
            style=style,
            preserve_formatting=not no_formatting,
            chunk_size=chunk_size,
        ))
        
        cli_ctx.info(f"📝 Output saved to: {result_path}")
        
    except ProcessorError as e:
        cli_ctx.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        cli_ctx.warning("🛑 Conversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        cli_ctx.error(f"Unexpected error: {str(e)}")
        if cli_ctx.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@doc2md.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory (default: input_dir/markdown)"
)
@click.option(
    "--pattern",
    default="*",
    help="File pattern to match (default: *)"
)
@click.option(
    "--ai-provider",
    type=click.Choice(["gemini", "ollama", "anthropic"]),
    help="AI provider to use (overrides config)"
)
@click.option(
    "--style",
    type=click.Choice(["technical", "academic", "business", "casual"]),
    default="technical",
    help="Output style"
)
@click.option(
    "--chunk-size",
    type=int,
    default=4000,
    help="Text chunk size for processing"
)
@click.option(
    "--no-formatting",
    is_flag=True,
    help="Don't preserve original formatting"
)
@click.option(
    "--max-concurrent",
    type=int,
    default=3,
    help="Maximum concurrent conversions"
)
@click.pass_obj
def batch(
    cli_ctx: CLIContext,
    input_dir: Path,
    output_dir: Path | None,
    pattern: str,
    ai_provider: str | None,
    style: str,
    chunk_size: int,
    no_formatting: bool,
    max_concurrent: int,
) -> None:
    """📁 Convert multiple documents in a directory
    
    **INPUT_DIR**: Directory containing documents to convert
    
    Recursively finds all supported documents in the directory and converts
    them to Markdown. The directory structure is preserved in the output.
    """
    try:
        processor = Doc2mdProcessor(cli_ctx)
        
        # Validate AI provider
        if ai_provider:
            if not processor.ai_client.test_provider(ai_provider):
                cli_ctx.error(f"AI provider '{ai_provider}' is not properly configured")
                cli_ctx.info("Run: claude-clis config init")
                sys.exit(1)
        
        # Run batch conversion
        results = asyncio.run(processor.batch_convert(
            input_dir=input_dir,
            output_dir=output_dir,
            pattern=pattern,
            ai_provider=ai_provider,
            style=style,
            preserve_formatting=not no_formatting,
            chunk_size=chunk_size,
            max_concurrent=max_concurrent,
        ))
        
        if results:
            cli_ctx.success(f"🎉 Successfully converted {len(results)} files")
            if cli_ctx.verbose:
                for path in results:
                    cli_ctx.info(f"   ✓ {path}")
        else:
            cli_ctx.warning("⚠️ No files were converted")
        
    except ProcessorError as e:
        cli_ctx.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        cli_ctx.warning("🛑 Batch conversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        cli_ctx.error(f"Unexpected error: {str(e)}")
        if cli_ctx.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@doc2md.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.pass_obj
def info(cli_ctx: CLIContext, file_path: Path) -> None:
    """ℹ️ Show information about a document
    
    **FILE_PATH**: Path to the document to analyze
    
    Displays metadata and structural information about the document
    without performing conversion.
    """
    try:
        processor = Doc2mdProcessor(cli_ctx)
        
        if not processor.is_supported_format(file_path):
            supported = ", ".join(processor.get_supported_formats())
            cli_ctx.error(f"Unsupported file format. Supported: {supported}")
            sys.exit(1)
        
        # Get file info
        extension = file_path.suffix.lower()
        file_size = file_path.stat().st_size
        
        cli_ctx.info(f"📄 Document Information: {file_path.name}")
        cli_ctx.info(f"   Format: {extension}")
        cli_ctx.info(f"   Size: {processor.cli_ctx.format_file_size(file_size)}")
        
        # Format-specific info
        if extension == '.pdf' and processor.pdf_reader:
            info_data = processor.pdf_reader.get_pdf_info(file_path)
            cli_ctx.info(f"   Pages: {info_data.get('pages', 'Unknown')}")
            cli_ctx.info(f"   Title: {info_data.get('title', 'Not set')}")
            cli_ctx.info(f"   Author: {info_data.get('author', 'Not set')}")
            cli_ctx.info(f"   Encrypted: {'Yes' if info_data.get('encrypted') else 'No'}")
            
        elif extension in ['.docx', '.doc'] and processor.word_reader:
            info_data = processor.word_reader.get_document_info(file_path)
            cli_ctx.info(f"   Paragraphs: {info_data.get('paragraphs', 'Unknown')}")
            cli_ctx.info(f"   Tables: {info_data.get('tables', 'Unknown')}")
            cli_ctx.info(f"   Title: {info_data.get('title', 'Not set')}")
            cli_ctx.info(f"   Author: {info_data.get('author', 'Not set')}")
        
        # Check readability
        readable = True
        try:
            content = asyncio.run(processor._extract_content(file_path))
            content_length = len(content.strip())
            cli_ctx.info(f"   Content length: {content_length:,} characters")
            if content_length == 0:
                readable = False
        except Exception:
            readable = False
        
        status = "✅ Readable" if readable else "❌ Not readable"
        cli_ctx.info(f"   Status: {status}")
        
    except Exception as e:
        cli_ctx.error(f"Failed to analyze document: {str(e)}")
        sys.exit(1)


@doc2md.command()
@click.pass_obj
def test(cli_ctx: CLIContext) -> None:
    """🧪 Test AI providers and document readers
    
    Checks the availability and configuration of all AI providers
    and document format readers.
    """
    processor = Doc2mdProcessor(cli_ctx)
    
    cli_ctx.info("🧪 Testing Claude CLI Tools - doc2md")
    
    # Test document readers
    cli_ctx.info("\n📚 Document Readers:")
    
    pdf_status = "✅ Available" if processor.pdf_reader else "❌ Not available"
    cli_ctx.info(f"   PDF: {pdf_status}")
    
    word_status = "✅ Available" if processor.word_reader else "❌ Not available"
    cli_ctx.info(f"   Word: {word_status}")
    
    cli_ctx.info("   Text/Markdown: ✅ Always available")
    
    # Test AI providers
    cli_ctx.info("\n🤖 AI Providers:")
    
    providers = processor.ai_client.get_available_providers()
    for provider in providers:
        try:
            is_configured = processor.ai_client.test_provider(provider)
            status = "✅ Configured" if is_configured else "❌ Not configured"
            cli_ctx.info(f"   {provider.title()}: {status}")
        except Exception as e:
            cli_ctx.info(f"   {provider.title()}: ❌ Error - {str(e)}")
    
    # Show current configuration
    current_provider = config_manager.get_ai_provider()
    cli_ctx.info(f"\n⚙️ Current AI Provider: {current_provider}")
    
    # Configuration tips
    cli_ctx.info("\n💡 Configuration Tips:")
    cli_ctx.info("   • Run 'claude-clis config init' for guided setup")
    cli_ctx.info("   • Set API keys with 'claude-clis config set ai.PROVIDER.api_key YOUR_KEY'")
    cli_ctx.info("   • Install missing dependencies with 'uv add PACKAGE'")


if __name__ == "__main__":
    doc2md()