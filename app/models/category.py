"""Category model for product types."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    """Category model for product types (battery, inverter, solar_panel, charge_controller)."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


# Default categories
DEFAULT_CATEGORIES = [
    {"name": "battery", "description": "Solar batteries and energy storage systems"},
    {"name": "inverter", "description": "Solar inverters for DC to AC conversion"},
    {"name": "solar_panel", "description": "Solar photovoltaic panels and modules"},
    {"name": "charge_controller", "description": "Charge controllers for battery management"},
]
