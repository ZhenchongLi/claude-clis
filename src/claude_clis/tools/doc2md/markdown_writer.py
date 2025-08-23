from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class MarkdownWriter:
    def __init__(self) -> None:
        pass

    def clean_markdown(self, content: str) -> str:
        """Clean and normalize markdown content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Fix heading spacing
        content = re.sub(r'\n(#{1,6})', r'\n\n\1', content)
        content = re.sub(r'(#{1,6}[^\n]*)\n([^\n#])', r'\1\n\n\2', content)
        
        # Fix list spacing
        content = re.sub(r'\n([*+-]|\d+\.)', r'\n\1', content)
        
        # Clean up code blocks
        content = re.sub(r'```(\w*)\n\n', r'```\1\n', content)
        content = re.sub(r'\n\n```', r'\n```', content)
        
        # Remove trailing whitespace
        lines = [line.rstrip() for line in content.split('\n')]
        content = '\n'.join(lines)
        
        # Ensure single newline at end
        content = content.rstrip() + '\n'
        
        return content

    def add_table_of_contents(self, content: str) -> str:
        """Generate and add table of contents"""
        # Find all headings
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        if len(headings) < 2:  # Don't add TOC for documents with few headings
            return content
        
        toc_lines = ["## Table of Contents\n"]
        
        for level_hashes, title in headings:
            level = len(level_hashes)
            if level > 1:  # Skip h1 as it's usually the document title
                indent = "  " * (level - 2)
                # Create anchor link
                anchor = re.sub(r'[^\w\s-]', '', title).strip()
                anchor = re.sub(r'\s+', '-', anchor).lower()
                toc_lines.append(f"{indent}- [{title}](#{anchor})")
        
        if len(toc_lines) > 1:
            toc_content = "\n".join(toc_lines) + "\n\n---\n\n"
            
            # Insert after first heading or at the beginning
            first_heading_match = re.search(r'^#\s+.+$', content, re.MULTILINE)
            if first_heading_match:
                insert_pos = first_heading_match.end()
                content = content[:insert_pos] + "\n\n" + toc_content + content[insert_pos:]
            else:
                content = toc_content + content
        
        return content

    def format_tables(self, content: str) -> str:
        """Improve table formatting"""
        # Find and format tables
        table_pattern = r'(\|[^\n]+\|(?:\n\|[^\n]*\|)*)'
        
        def format_table(match: re.Match[str]) -> str:
            table_text = match.group(1)
            lines = table_text.strip().split('\n')
            
            if len(lines) < 2:
                return table_text
            
            # Parse table
            rows = []
            for line in lines:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
            
            if not rows:
                return table_text
            
            # Calculate column widths
            max_cols = max(len(row) for row in rows)
            col_widths = []
            
            for col in range(max_cols):
                max_width = 0
                for row in rows:
                    if col < len(row):
                        max_width = max(max_width, len(row[col]))
                col_widths.append(max(max_width, 3))
            
            # Format table
            formatted_lines = []
            for i, row in enumerate(rows):
                # Pad row to match max columns
                while len(row) < max_cols:
                    row.append("")
                
                # Format cells
                formatted_cells = []
                for j, cell in enumerate(row):
                    width = col_widths[j]
                    formatted_cells.append(f" {cell:<{width}} ")
                
                formatted_line = "|" + "|".join(formatted_cells) + "|"
                formatted_lines.append(formatted_line)
                
                # Add separator after header
                if i == 0 and len(rows) > 1:
                    separator_cells = [f" {'-' * col_widths[j]} " for j in range(max_cols)]
                    separator_line = "|" + "|".join(separator_cells) + "|"
                    formatted_lines.append(separator_line)
            
            return "\n".join(formatted_lines)
        
        return re.sub(table_pattern, format_table, content, flags=re.MULTILINE)

    def add_metadata(self, content: str, metadata: dict[str, Any]) -> str:
        """Add YAML frontmatter metadata"""
        if not metadata:
            return content
        
        frontmatter_lines = ["---"]
        for key, value in metadata.items():
            if isinstance(value, str):
                frontmatter_lines.append(f"{key}: \"{value}\"")
            else:
                frontmatter_lines.append(f"{key}: {value}")
        frontmatter_lines.extend(["---", ""])
        
        frontmatter = "\n".join(frontmatter_lines)
        return frontmatter + content

    def write_markdown(
        self, 
        content: str, 
        output_path: Path | str,
        add_toc: bool = False,
        clean: bool = True,
        metadata: dict[str, Any] | None = None,
        format_tables: bool = True,
    ) -> None:
        """Write markdown content to file with optional enhancements"""
        output_path = Path(output_path)
        
        # Apply enhancements
        if clean:
            content = self.clean_markdown(content)
        
        if format_tables:
            content = self.format_tables(content)
        
        if add_toc:
            content = self.add_table_of_contents(content)
        
        if metadata:
            content = self.add_metadata(content, metadata)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def validate_markdown(self, content: str) -> list[str]:
        """Validate markdown and return list of issues"""
        issues = []
        
        # Check for unbalanced code blocks
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            issues.append("Unbalanced code blocks (``` count is odd)")
        
        # Check for malformed tables
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '|' in line and line.count('|') < 2:
                issues.append(f"Line {i}: Possible malformed table")
        
        # Check for missing heading hierarchy
        heading_levels = []
        for match in re.finditer(r'^(#{1,6})', content, re.MULTILINE):
            level = len(match.group(1))
            heading_levels.append(level)
        
        for i in range(1, len(heading_levels)):
            if heading_levels[i] > heading_levels[i-1] + 1:
                issues.append(f"Heading hierarchy skip detected (jumped from h{heading_levels[i-1]} to h{heading_levels[i]})")
        
        # Check for empty links or images
        empty_links = re.findall(r'\[([^\]]*)\]\(\s*\)', content)
        if empty_links:
            issues.append(f"Empty links found: {len(empty_links)} instances")
        
        empty_images = re.findall(r'!\[([^\]]*)\]\(\s*\)', content)
        if empty_images:
            issues.append(f"Empty images found: {len(empty_images)} instances")
        
        return issues