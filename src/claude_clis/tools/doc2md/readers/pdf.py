from __future__ import annotations

from pathlib import Path

try:
    import fitz  # PyMuPDF
    import pymupdf4llm
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFReaderError(Exception):
    pass


class PDFReader:
    def __init__(self) -> None:
        if not PYMUPDF_AVAILABLE:
            raise PDFReaderError(
                "PyMuPDF is not available. Install with: pip install pymupdf pymupdf4llm"
            )

    def read_pdf(self, file_path: Path | str) -> str:
        """Read PDF content and extract text"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise PDFReaderError(f"File not found: {file_path}")
        
        if not file_path.suffix.lower() == '.pdf':
            raise PDFReaderError(f"Not a PDF file: {file_path}")
        
        try:
            # Use pymupdf4llm for better LLM-optimized extraction
            content = pymupdf4llm.to_markdown(str(file_path))
            return content
        except Exception as e:
            # Fallback to basic PyMuPDF extraction
            try:
                return self._extract_with_pymupdf(file_path)
            except Exception as fallback_e:
                raise PDFReaderError(
                    f"Failed to read PDF: {str(e)}. Fallback also failed: {str(fallback_e)}"
                ) from e

    def _extract_with_pymupdf(self, file_path: Path) -> str:
        """Fallback extraction using basic PyMuPDF"""
        doc = fitz.open(str(file_path))
        content = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            if text.strip():
                content.append(f"## Page {page_num + 1}\n\n{text}")
        
        doc.close()
        
        if not content:
            raise PDFReaderError("No readable text found in PDF")
        
        return "\n\n".join(content)

    def get_pdf_info(self, file_path: Path | str) -> dict[str, str | int]:
        """Get PDF metadata and information"""
        file_path = Path(file_path)
        
        try:
            doc = fitz.open(str(file_path))
            metadata = doc.metadata
            
            info = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "pages": len(doc),
                "encrypted": doc.needs_pass,
            }
            
            doc.close()
            return info
            
        except Exception as e:
            raise PDFReaderError(f"Failed to get PDF info: {str(e)}") from e

    def is_pdf_readable(self, file_path: Path | str) -> bool:
        """Check if PDF can be read (not password protected, etc.)"""
        try:
            doc = fitz.open(str(file_path))
            if doc.needs_pass:
                doc.close()
                return False
            
            # Try to read first page
            if len(doc) > 0:
                page = doc.load_page(0)
                text = page.get_text()
                doc.close()
                return len(text.strip()) > 0
            
            doc.close()
            return False
            
        except Exception:
            return False