"""Company model for solar product manufacturers."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Company(Base):
    """Company model representing solar product manufacturers."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    country = Column(String(100))
    website = Column(String(500))
    support_email = Column(String(255))
    support_phone = Column(String(50))
    warranty_info = Column(Text)
    avg_response_time_hours = Column(Float, default=0.0)
    support_rating = Column(Float, default=0.0)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="company")
    metrics = relationship("CompanyMetric", back_populates="company")
    reviews = relationship("Review", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', verified={self.verified})>"
