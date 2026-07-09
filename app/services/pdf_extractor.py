"""PDF text extraction service using pdfplumber or PyMuPDF."""
import logging
from typing import Optional

import fitz  # PyMuPDF
from sqlalchemy.orm import Session

from app.models.document import Document, ExtractionStatus
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PDFExtractor:
    """Service for extracting text from PDF documents."""

    def __init__(self, db: Session):
        """Initialize the PDF extractor with a database session."""
        self.db = db

    def extract_text_from_file(self, file_path: str) -> tuple[str, Optional[str]]:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Tuple of (extracted_text, error_message)
        """
        try:
            text_parts = []
            
            # Open PDF document
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            doc.close()
            
            if not text_parts:
                return "", "No text found in PDF"
            
            full_text = "\n\n".join(text_parts)
            return full_text, None
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return "", f"Extraction failed: {str(e)}"

    def extract_text_from_bytes(self, pdf_bytes: bytes) -> tuple[str, Optional[str]]:
        """
        Extract text from PDF bytes.

        Args:
            pdf_bytes: PDF file content as bytes

        Returns:
            Tuple of (extracted_text, error_message)
        """
        try:
            text_parts = []
            
            # Open PDF document from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            doc.close()
            
            if not text_parts:
                return "", "No text found in PDF"
            
            full_text = "\n\n".join(text_parts)
            return full_text, None
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF bytes: {str(e)}")
            return "", f"Extraction failed: {str(e)}"

    def process_document(self, document_id: int) -> tuple[bool, Optional[str]]:
        """
        Process a document by extracting its text.

        Args:
            document_id: ID of the document to process

        Returns:
            Tuple of (success, error_message)
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            return False, "Document not found"
        
        # Get file path from URL
        file_path = document.file_url
        
        # Handle both local paths and URLs
        if file_path.startswith("http"):
            # For URLs, we'd need to download first
            # For now, assume local file
            return False, "URL-based extraction not yet supported"
        
        # Extract text
        text, error = self.extract_text_from_file(file_path)
        
        if error:
            document.extraction_status = ExtractionStatus.FAILED
            document.extraction_error = error
            self.db.commit()
            return False, error
        
        # Update document with extracted text
        document.extracted_text = text
        document.extraction_status = ExtractionStatus.SUCCESS
        document.extraction_error = None
        self.db.commit()
        
        return True, None

    def batch_process_documents(self, document_ids: list[int]) -> dict[int, tuple[bool, Optional[str]]]:
        """
        Process multiple documents in batch.

        Args:
            document_ids: List of document IDs to process

        Returns:
            Dictionary mapping document_id to (success, error_message)
        """
        results = {}
        for doc_id in document_ids:
            success, error = self.process_document(doc_id)
            results[doc_id] = (success, error)
        return results
