"""Pydantic schemas for reviews."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ReviewBase(BaseModel):
    """Base review schema."""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    issue_type: Optional[str] = Field(None, max_length=100)
    reviewer_name: Optional[str] = Field(None, max_length=100)
    reviewer_email: Optional[EmailStr] = None
    is_verified_purchase: bool = False


class ReviewCreate(ReviewBase):
    """Schema for creating a new review."""
    product_id: Optional[int] = None
    company_id: Optional[int] = None

    @field_validator('product_id', 'company_id')
    @classmethod
    def at_least_one_target(cls, v, info):
        """Ensure at least product_id or company_id is provided."""
        return v


class ReviewUpdate(BaseModel):
    """Schema for updating a review."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    issue_type: Optional[str] = Field(None, max_length=100)


class ReviewResponse(ReviewBase):
    """Schema for review response."""
    id: int
    product_id: Optional[int] = None
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Schema for review list response."""
    total: int
    average_rating: float
    reviews: List[ReviewResponse]
