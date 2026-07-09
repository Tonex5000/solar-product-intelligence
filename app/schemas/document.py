"""Pydantic schemas for documents."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.document import DocumentType, ExtractionStatus


class DocumentBase(BaseModel):
    """Base document schema."""
    type: DocumentType


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    product_id: int
    file_url: str = Field(..., min_length=1)


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    extracted_text: Optional[str] = None
    extraction_status: Optional[ExtractionStatus] = None
    extraction_error: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    product_id: int
    file_url: str
    extraction_status: ExtractionStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """Schema for detailed document response with extracted text."""
    extracted_text: Optional[str] = None
    extraction_error: Optional[str] = None
