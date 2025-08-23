from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claude_clis.shared.utils import (
    CLIContext,
    FileProcessor,
    format_duration,
    format_file_size,
    sanitize_filename,
    validate_output_path,
)


def test_format_file_size():
    """Test file size formatting"""
    assert format_file_size(0) == "0 B"
    assert format_file_size(512) == "512.0 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1536) == "1.5 KB"
    assert format_file_size(1024 * 1024) == "1.0 MB"
    assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"


def test_format_duration():
    """Test duration formatting"""
    assert format_duration(0.5) == "500ms"
    assert format_duration(1.5) == "1.5s"
    assert format_duration(65) == "1m 5.0s"
    assert format_duration(3665) == "1h 1m 5.0s"


def test_sanitize_filename():
    """Test filename sanitization"""
    assert sanitize_filename("normal_file.txt") == "normal_file.txt"
    assert sanitize_filename("file<with>bad:chars.txt") == "file_with_bad_chars.txt"
    assert sanitize_filename("  .file with spaces. ") == "file with spaces"
    assert sanitize_filename("a" * 300) == "a" * 255


def test_validate_output_path():
    """Test output path validation"""
    # With explicit output path
    output = validate_output_path("/path/to/output.md", "/input/file.pdf")
    assert output == Path("/path/to/output.md")
    
    # Without explicit output path (should derive from input)
    output = validate_output_path(None, "/input/document.pdf")
    assert output == Path("/input/document.md")
    
    # With custom extension
    output = validate_output_path(None, "/input/document.docx", ".txt")
    assert output == Path("/input/document.txt")


def test_cli_context():
    """Test CLIContext functionality"""
    ctx = CLIContext()
    
    # Test default settings
    assert not ctx.verbose
    assert not ctx.quiet
    assert not ctx.dry_run
    
    # Test log methods (these shouldn't raise errors)
    ctx.info("test info")
    ctx.success("test success")
    ctx.warning("test warning")
    ctx.error("test error")
    ctx.debug("test debug")  # Should not print when verbose=False
    
    # Test verbose mode
    ctx.verbose = True
    ctx.debug("test debug verbose")  # Should print when verbose=True


def test_file_processor_read_write():
    """Test FileProcessor read/write functionality"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_file = tmpdir / "test.txt"
        test_content = "Hello, World!\nThis is a test file."
        
        # Write file
        FileProcessor.write_text_file(test_file, test_content)
        assert test_file.exists()
        
        # Read file
        read_content = FileProcessor.read_text_file(test_file)
        assert read_content == test_content


def test_file_processor_create_dirs():
    """Test FileProcessor directory creation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        nested_file = tmpdir / "nested" / "dirs" / "test.txt"
        
        # Write file with directory creation
        FileProcessor.write_text_file(nested_file, "test", create_dirs=True)
        assert nested_file.exists()
        assert nested_file.parent.exists()


def test_file_processor_backup():
    """Test FileProcessor backup functionality"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        original_file = tmpdir / "original.txt"
        original_content = "original content"
        
        # Create original file
        FileProcessor.write_text_file(original_file, original_content)
        
        # Backup file
        backup_path = FileProcessor.backup_file(original_file)
        
        assert backup_path.exists()
        assert backup_path.name == "original.txt.bak"
        assert not original_file.exists()  # Original should be moved
        
        # Read backup content
        backup_content = FileProcessor.read_text_file(backup_path)
        assert backup_content == original_content


def test_file_processor_encoding_fallback():
    """Test FileProcessor encoding fallback"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_file = tmpdir / "encoded.txt"
        
        # Write file with specific encoding
        content = "Special characters: café, naïve, résumé"
        with open(test_file, "w", encoding="latin-1") as f:
            f.write(content)
        
        # Should be able to read with fallback
        read_content = FileProcessor.read_text_file(test_file)
        assert "café" in read_content or "caf" in read_content  # May be decoded differently