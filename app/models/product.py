"""Product model for solar products."""
import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class ValidationStatus(str, enum.Enum):
    """Product validation status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Product(Base):
    """Product model representing solar products with datasheet requirements."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    datasheet_file_url = Column(String(500), nullable=False)  # REQUIRED - no datasheet = no product
    manual_file_url = Column(String(500), nullable=True)
    validation_status = Column(
        Enum(ValidationStatus),
        default=ValidationStatus.PENDING,
        nullable=False
    )
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="products")
    category = relationship("Category", back_populates="products")
    documents = relationship("Document", back_populates="product", cascade="all, delete-orphan")
    specifications = relationship(
        "ProductSpecification",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    reviews = relationship("Review", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, model='{self.model_name}', status='{self.validation_status}')>"
