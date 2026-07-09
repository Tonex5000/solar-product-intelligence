"""Pydantic schemas for company metrics."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CompanyMetricBase(BaseModel):
    """Base company metric schema."""
    response_time_hours: float = Field(ge=0.0)
    issue_resolution_rate: float = Field(ge=0.0, le=100.0)
    failure_rate: float = Field(ge=0.0, le=100.0)
    user_rating: float = Field(ge=0.0, le=5.0)
    total_reviews: int = Field(ge=0)


class CompanyMetricCreate(CompanyMetricBase):
    """Schema for creating a new company metric."""
    company_id: int


class CompanyMetricUpdate(BaseModel):
    """Schema for updating a company metric."""
    response_time_hours: Optional[float] = Field(None, ge=0.0)
    issue_resolution_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    failure_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    user_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    total_reviews: Optional[int] = Field(None, ge=0)


class CompanyMetricResponse(CompanyMetricBase):
    """Schema for company metric response."""
    id: int
    company_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True
