"""Pydantic schemas for product specifications."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SpecificationBase(BaseModel):
    """Base specification schema."""
    spec_key: str = Field(..., min_length=1, max_length=100)
    spec_value: str = Field(..., min_length=1, max_length=255)
    unit: Optional[str] = Field(None, max_length=50)


class SpecificationCreate(SpecificationBase):
    """Schema for creating a new specification."""
    product_id: int
    confidence_score: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    source_location: Optional[str] = None


class SpecificationUpdate(BaseModel):
    """Schema for updating a specification."""
    spec_value: Optional[str] = Field(None, min_length=1, max_length=255)
    unit: Optional[str] = Field(None, max_length=50)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class SpecificationResponse(SpecificationBase):
    """Schema for specification response."""
    id: int
    product_id: int
    confidence_score: float
    source_location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SpecificationListResponse(BaseModel):
    """Schema for specification list response."""
    total: int
    specifications: List[SpecificationResponse]


class SpecificationGroupedResponse(BaseModel):
    """Schema for grouped specifications by key prefix."""
    groups: dict[str, List[SpecificationResponse]]
