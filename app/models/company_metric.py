"""Company metrics model for tracking company performance."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class CompanyMetric(Base):
    """Company metrics model for tracking performance over time."""

    __tablename__ = "company_metrics"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    response_time_hours = Column(Float, default=0.0)
    issue_resolution_rate = Column(Float, default=0.0)  # Percentage 0-100
    failure_rate = Column(Float, default=0.0)  # Percentage 0-100
    user_rating = Column(Float, default=0.0)  # 0-5 stars
    total_reviews = Column(Integer, default=0)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="metrics")

    def __repr__(self):
        return f"<CompanyMetric(id={self.id}, company_id={self.company_id}, rating={self.user_rating})>"
