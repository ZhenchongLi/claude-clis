from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claude_clis.tools.doc2md.markdown_writer import MarkdownWriter


@pytest.fixture
def writer():
    """Create a MarkdownWriter instance"""
    return MarkdownWriter()


def test_clean_markdown(writer):
    """Test markdown cleaning functionality"""
    messy_content = """# Title


Some content with     excessive   spacing.



## Section

Another section.
```python

code_here()
```


"""
    
    cleaned = writer.clean_markdown(messy_content)
    
    # Should have normalized spacing
    assert cleaned.count('\n\n\n') == 0
    assert '## Section\n\nAnother' in cleaned
    assert '```python\ncode_here()' in cleaned


def test_format_tables(writer):
    """Test table formatting"""
    unformatted_table = """| Name | Age | City |
|---|---|---|
| John | 25 | New York |
| Jane | 30 | Los Angeles |"""
    
    formatted = writer.format_tables(unformatted_table)
    
    # Should have consistent column widths
    lines = formatted.split('\n')
    assert len(lines) >= 3
    # All lines should have same length (approximately)
    line_lengths = [len(line) for line in lines if line.strip()]
    assert max(line_lengths) - min(line_lengths) <= 2  # Allow small variance


def test_add_table_of_contents(writer):
    """Test table of contents generation"""
    content = """# Main Title

## Introduction

Some intro text.

### Subsection

More content.

## Conclusion

Final thoughts."""
    
    with_toc = writer.add_table_of_contents(content)
    
    assert "## Table of Contents" in with_toc
    assert "- [Introduction](#introduction)" in with_toc
    assert "  - [Subsection](#subsection)" in with_toc
    assert "- [Conclusion](#conclusion)" in with_toc


def test_add_table_of_contents_short_doc(writer):
    """Test that TOC is not added for short documents"""
    short_content = """# Title

Just one section."""
    
    result = writer.add_table_of_contents(short_content)
    assert "Table of Contents" not in result
    assert result == short_content


def test_add_metadata(writer):
    """Test YAML frontmatter addition"""
    content = "# Document\n\nContent here."
    metadata = {
        "title": "Test Document",
        "author": "Test Author",
        "date": "2024-01-01",
        "draft": False
    }
    
    with_metadata = writer.add_metadata(content, metadata)
    
    assert with_metadata.startswith("---\n")
    assert 'title: "Test Document"' in with_metadata
    assert 'author: "Test Author"' in with_metadata
    assert 'draft: False' in with_metadata
    assert "# Document" in with_metadata


def test_validate_markdown(writer):
    """Test markdown validation"""
    # Valid markdown
    valid_md = """# Title

## Section

Some text with `inline code` and:

```python
def hello():
    return "world"
```

| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    
    issues = writer.validate_markdown(valid_md)
    assert len(issues) == 0
    
    # Invalid markdown
    invalid_md = """# Title

```python
unclosed code block

| Incomplete table
Missing [link]()
![missing image]()

##### H5 after H1 (skip)
"""
    
    issues = writer.validate_markdown(invalid_md)
    assert len(issues) > 0
    assert any("Unbalanced code blocks" in issue for issue in issues)
    assert any("Empty links" in issue for issue in issues)
    assert any("Empty images" in issue for issue in issues)
    assert any("Heading hierarchy skip" in issue for issue in issues)


def test_write_markdown(writer):
    """Test writing markdown to file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_file = tmpdir / "test.md"
        
        content = "# Test\n\nContent here."
        metadata = {"title": "Test Doc"}
        
        writer.write_markdown(
            content=content,
            output_path=output_file,
            add_toc=False,
            clean=True,
            metadata=metadata,
            format_tables=True
        )
        
        assert output_file.exists()
        
        # Read and verify content
        with open(output_file, encoding="utf-8") as f:
            written_content = f.read()
        
        assert "---" in written_content  # Metadata present
        assert 'title: "Test Doc"' in written_content
        assert "# Test" in written_content


def test_write_markdown_with_all_features(writer):
    """Test writing markdown with all enhancement features"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_file = tmpdir / "enhanced.md"
        
        content = """# Main Document

## Section 1

Content for section 1.

### Subsection

More content.

## Section 2

Final section.

|Name|Age|
|---|---|
|John|25|
"""
        
        metadata = {"title": "Enhanced Doc", "author": "Test"}
        
        writer.write_markdown(
            content=content,
            output_path=output_file,
            add_toc=True,
            clean=True,
            metadata=metadata,
            format_tables=True
        )
        
        assert output_file.exists()
        
        with open(output_file, encoding="utf-8") as f:
            result = f.read()
        
        # Should have all features
        assert "---" in result  # Metadata
        assert "Table of Contents" in result  # TOC
        assert "| Name | Age |" in result  # Formatted table
        assert result.endswith("\n")  # Proper ending