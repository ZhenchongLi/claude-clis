from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any

from ...shared.ai_client import AIClient, DocumentProcessor
from ...shared.config import config_manager
from ...shared.utils import CLIContext, format_duration, format_file_size
from .readers.pdf import PDFReader, PDFReaderError
from .readers.word import WordReader, WordReaderError


class ProcessorError(Exception):
    pass


class Doc2mdProcessor:
    def __init__(self, cli_ctx: CLIContext) -> None:
        self.cli_ctx = cli_ctx
        self.ai_client = AIClient(config_manager)
        self.doc_processor = DocumentProcessor(self.ai_client)
        
        # Initialize readers
        try:
            self.pdf_reader = PDFReader()
        except PDFReaderError as e:
            self.cli_ctx.warning(f"PDF reader unavailable: {e}")
            self.pdf_reader = None
            
        try:
            self.word_reader = WordReader()
        except WordReaderError as e:
            self.cli_ctx.warning(f"Word reader unavailable: {e}")
            self.word_reader = None

    def get_supported_formats(self) -> list[str]:
        """Get list of supported document formats"""
        formats = []
        if self.pdf_reader:
            formats.extend(['.pdf'])
        if self.word_reader:
            formats.extend(['.docx', '.doc'])
        formats.extend(['.txt', '.md'])  # Always supported
        return formats

    def is_supported_format(self, file_path: Path | str) -> bool:
        """Check if file format is supported"""
        extension = Path(file_path).suffix.lower()
        return extension in self.get_supported_formats()

    async def convert_file(
        self,
        input_file: Path | str,
        output_file: Path | str | None = None,
        ai_provider: str | None = None,
        style: str = "technical",
        preserve_formatting: bool = True,
        chunk_size: int = 4000,
        **kwargs: Any
    ) -> Path:
        """Convert a single document to Markdown"""
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise ProcessorError(f"Input file not found: {input_path}")
        
        if not self.is_supported_format(input_path):
            supported = ", ".join(self.get_supported_formats())
            raise ProcessorError(
                f"Unsupported file format: {input_path.suffix}. "
                f"Supported formats: {supported}"
            )
        
        # Determine output path
        if output_file:
            output_path = Path(output_file)
        else:
            output_path = input_path.with_suffix('.md')
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        file_size = input_path.stat().st_size
        
        self.cli_ctx.info(f"📄 Processing: {input_path.name} ({format_file_size(file_size)})")
        self.cli_ctx.debug(f"Input: {input_path}")
        self.cli_ctx.debug(f"Output: {output_path}")
        self.cli_ctx.debug(f"AI Provider: {ai_provider or 'default'}")
        self.cli_ctx.debug(f"Style: {style}")
        
        try:
            # Extract content
            content = await self._extract_content(input_path)
            
            if not content.strip():
                raise ProcessorError("No readable content found in document")
            
            self.cli_ctx.debug(f"Extracted content length: {len(content)} characters")
            
            # Process with AI
            self.cli_ctx.info("🤖 Converting to Markdown...")
            markdown_content = await self.doc_processor.process_large_content(
                content=content,
                provider=ai_provider,
                chunk_size=chunk_size,
                style=style,
                preserve_formatting=preserve_formatting,
                **kwargs
            )
            
            # Add metadata header
            metadata = self._generate_metadata(input_path, ai_provider or "default", style)
            final_content = f"{metadata}\n\n{markdown_content}"
            
            # Save output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            duration = time.time() - start_time
            output_size = output_path.stat().st_size
            
            self.cli_ctx.success(
                f"✅ Converted {input_path.name} → {output_path.name} "
                f"({format_file_size(output_size)}) in {format_duration(duration)}"
            )
            
            return output_path
            
        except Exception as e:
            duration = time.time() - start_time
            self.cli_ctx.error(
                f"❌ Failed to convert {input_path.name} after {format_duration(duration)}: {str(e)}"
            )
            raise ProcessorError(f"Conversion failed: {str(e)}") from e

    async def batch_convert(
        self,
        input_dir: Path | str,
        output_dir: Path | str | None = None,
        pattern: str = "*",
        ai_provider: str | None = None,
        style: str = "technical",
        preserve_formatting: bool = True,
        chunk_size: int = 4000,
        max_concurrent: int = 3,
        **kwargs: Any
    ) -> list[Path]:
        """Convert multiple documents in batch"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise ProcessorError(f"Input directory not found: {input_path}")
        
        if not input_path.is_dir():
            raise ProcessorError(f"Input path is not a directory: {input_path}")
        
        # Find files
        files = []
        for file_path in input_path.rglob(pattern):
            if file_path.is_file() and self.is_supported_format(file_path):
                files.append(file_path)
        
        if not files:
            supported = ", ".join(self.get_supported_formats())
            raise ProcessorError(
                f"No supported files found in {input_path}. "
                f"Supported formats: {supported}"
            )
        
        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = input_path / "markdown"
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.cli_ctx.info(f"📁 Found {len(files)} files to convert")
        self.cli_ctx.info(f"📤 Output directory: {output_path}")
        
        # Process files with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []
        
        async def convert_with_semaphore(file: Path) -> Path | None:
            async with semaphore:
                try:
                    output_file = output_path / f"{file.stem}.md"
                    return await self.convert_file(
                        input_file=file,
                        output_file=output_file,
                        ai_provider=ai_provider,
                        style=style,
                        preserve_formatting=preserve_formatting,
                        chunk_size=chunk_size,
                        **kwargs
                    )
                except ProcessorError:
                    return None
        
        # Create tasks
        for file in files:
            tasks.append(convert_with_semaphore(file))
        
        # Execute with progress tracking
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Process results
        successful = []
        failed = 0
        
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            elif result:
                successful.append(result)
            else:
                failed += 1
        
        self.cli_ctx.success(
            f"✅ Batch conversion completed in {format_duration(duration)}"
        )
        self.cli_ctx.info(f"   Success: {len(successful)} files")
        if failed > 0:
            self.cli_ctx.warning(f"   Failed: {failed} files")
        
        return successful

    async def _extract_content(self, file_path: Path) -> str:
        """Extract content from various file formats"""
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            if not self.pdf_reader:
                raise ProcessorError("PDF reader not available")
            return self.pdf_reader.read_pdf(file_path)
            
        elif extension in ['.docx', '.doc']:
            if not self.word_reader:
                raise ProcessorError("Word reader not available")
            return self.word_reader.read_docx(file_path)
            
        elif extension in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        else:
            raise ProcessorError(f"Unsupported file format: {extension}")

    def _generate_metadata(self, input_file: Path, ai_provider: str, style: str) -> str:
        """Generate metadata header for converted document"""
        return f"""<!-- 
This document was converted from {input_file.name} to Markdown
using Claude CLI Tools with the following settings:

- AI Provider: {ai_provider}
- Style: {style}
- Original file: {input_file.name}
- Conversion date: {time.strftime('%Y-%m-%d %H:%M:%S')}

Generated by Claude CLI Tools - https://github.com/your-username/claude-clis
-->"""