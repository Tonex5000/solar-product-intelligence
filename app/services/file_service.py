"""File handling service for document uploads."""
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import Document, DocumentType
from app.models.product import Product

settings = get_settings()


class FileService:
    """Service for handling file uploads and storage."""

    def __init__(self, db: Session):
        """Initialize file service with database session."""
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure upload directories exist."""
        (self.upload_dir / "datasheets").mkdir(parents=True, exist_ok=True)
        (self.upload_dir / "manuals").mkdir(parents=True, exist_ok=True)

    def _get_extension(self, filename: str) -> str:
        """Get file extension from filename."""
        return os.path.splitext(filename)[1].lower()

    def _validate_file(self, file: UploadFile, allowed_extensions: set) -> Tuple[bool, Optional[str]]:
        """Validate uploaded file."""
        if not file.filename:
            return False, "No filename provided"
        
        extension = self._get_extension(file.filename)
        
        if extension not in allowed_extensions:
            return False, f"File type {extension} not allowed. Allowed: {allowed_extensions}"
        
        return True, None

    async def save_upload(
        self,
        file: UploadFile,
        document_type: DocumentType,
        product_id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Save an uploaded file to disk.

        Args:
            file: Uploaded file
            document_type: Type of document (datasheet or manual)
            product_id: ID of the associated product

        Returns:
            Tuple of (file_url, error_message)
        """
        # Determine allowed extensions based on document type
        allowed = settings.ALLOWED_EXTENSIONS
        
        # Validate file
        is_valid, error = self._validate_file(file, allowed)
        if not is_valid:
            return None, error
        
        # Generate unique filename
        extension = self._get_extension(file.filename)
        unique_filename = f"{product_id}_{document_type.value}_{uuid.uuid4().hex}{extension}"
        
        # Determine subdirectory
        subdir = "datasheets" if document_type == DocumentType.DATASHEET else "manuals"
        file_path = self.upload_dir / subdir / unique_filename
        
        # Save file
        try:
            content = await file.read()
            
            # Check file size
            max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
            if len(content) > max_size:
                return None, f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Return the file URL (relative path)
            file_url = str(file_path)
            return file_url, None
            
        except Exception as e:
            return None, f"Failed to save file: {str(e)}"

    def delete_file(self, file_url: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from disk.

        Args:
            file_url: URL/path of the file to delete

        Returns:
            Tuple of (success, error_message)
        """
        try:
            file_path = Path(file_url)
            if file_path.exists():
                file_path.unlink()
            return True, None
        except Exception as e:
            return False, f"Failed to delete file: {str(e)}"

    def get_file_path(self, document: Document) -> Optional[Path]:
        """Get the file path for a document."""
        if not document.file_url:
            return None
        
        file_path = Path(document.file_url)
        if file_path.exists():
            return file_path
        
        return None

    def file_exists(self, file_url: str) -> bool:
        """Check if a file exists at the given URL."""
        return Path(file_url).exists()

    def get_file_size(self, file_url: str) -> Optional[int]:
        """Get the size of a file in bytes."""
        file_path = Path(file_url)
        if file_path.exists():
            return file_path.stat().st_size
        return None
