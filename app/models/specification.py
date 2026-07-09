"""Product specification model for flexible key-value specs."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductSpecification(Base):
    """Product specification model storing flexible key-value specifications."""

    __tablename__ = "product_specifications"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    spec_key = Column(String(100), nullable=False, index=True)
    spec_value = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=True)
    confidence_score = Column(Float, default=1.0)  # 0.0 to 1.0 confidence in extraction
    source_location = Column(String(255), nullable=True)  # Page/section in document
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="specifications")

    def __repr__(self):
        return f"<ProductSpecification(id={self.id}, key='{self.spec_key}', value='{self.spec_value}')>"


# Required specifications by category for validation
REQUIRED_SPECS_BY_CATEGORY = {
    "battery": ["voltage", "capacity", "cycle_life"],
    "inverter": ["rated_power", "battery_voltage_range", "max_charge_current"],
    "solar_panel": ["wattage", "Voc", "Isc"],
    "charge_controller": ["max_input_voltage", "rated_current", "efficiency"],
}
