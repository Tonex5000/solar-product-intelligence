"""Pydantic schemas for products."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.models.product import ValidationStatus


class ProductBase(BaseModel):
    """Base product schema."""
    model_name: str = Field(..., min_length=1, max_length=100)
    product_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    company_id: int
    category_id: int
    datasheet_file_url: str = Field(..., min_length=1, description="REQUIRED: URL to official datasheet")
    manual_file_url: Optional[str] = None

    @validator('datasheet_file_url')
    def datasheet_required(cls, v):
        """Ensure datasheet URL is always provided."""
        if not v or v.strip() == "":
            raise ValueError("Product MUST have an official datasheet URL")
        return v


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    model_name: Optional[str] = Field(None, min_length=1, max_length=100)
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    datasheet_file_url: Optional[str] = None
    manual_file_url: Optional[str] = None
    validation_status: Optional[ValidationStatus] = None
    is_verified: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: int
    company_id: int
    category_id: int
    datasheet_file_url: str
    manual_file_url: Optional[str] = None
    validation_status: ValidationStatus
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    """Schema for detailed product response with relationships."""
    company_name: Optional[str] = None
    category_name: Optional[str] = None


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    total: int
    products: List[ProductResponse]
