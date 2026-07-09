"""Document model for product datasheets and manuals."""
import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class DocumentType(str, enum.Enum):
    """Document type enum."""
    DATASHEET = "datasheet"
    MANUAL = "manual"


class ExtractionStatus(str, enum.Enum):
    """Document extraction status enum."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Document(Base):
    """Document model for storing product datasheets and manuals."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    type = Column(Enum(DocumentType), nullable=False)
    file_url = Column(String(500), nullable=False)
    extracted_text = Column(Text)  # Full text for future AI Q&A
    extraction_status = Column(
        Enum(ExtractionStatus),
        default=ExtractionStatus.PENDING
    )
    extraction_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, product_id={self.product_id}, type='{self.type}')>"
