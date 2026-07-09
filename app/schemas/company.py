"""Pydantic schemas for companies."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str = Field(..., min_length=1, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = Field(None, max_length=50)
    warranty_info: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = Field(None, max_length=50)
    warranty_info: Optional[str] = None
    verified: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: int
    avg_response_time_hours: float
    support_rating: float
    verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Schema for paginated company list response."""
    total: int
    companies: List[CompanyResponse]
