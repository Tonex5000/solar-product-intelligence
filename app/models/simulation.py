"""Simulation History model for storing simulation results."""
import json
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class SimulationStatusEnum(str, Enum):
    """Simulation status enum for database."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationHistory(Base):
    """Model for storing simulation history."""

    __tablename__ = "simulation_history"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), default=SimulationStatusEnum.PENDING.value, nullable=False)
    
    # Input parameters
    battery_id = Column(Integer, nullable=False)
    inverter_id = Column(Integer, nullable=False)
    panel_id = Column(Integer, nullable=False)
    charge_controller_id = Column(Integer, nullable=False)
    load_watts = Column(Integer, nullable=False)
    daily_usage_hours = Column(Integer, nullable=False)
    simulation_days = Column(Integer, nullable=False)
    location = Column(String(100), default="default")
    avg_sun_hours = Column(Integer, default=5)
    
    # Summary results (JSON stored)
    summary_json = Column(Text, nullable=True)
    
    # Full results (JSON stored for later retrieval)
    full_results_json = Column(Text, nullable=True)
    
    # Recommendations (JSON stored)
    recommendations_json = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # User reference (optional)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="simulations")

    def __repr__(self):
        return f"<SimulationHistory(id={self.id}, status='{self.status}', created_at={self.created_at})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "status": self.status,
            "battery_id": self.battery_id,
            "inverter_id": self.inverter_id,
            "panel_id": self.panel_id,
            "charge_controller_id": self.charge_controller_id,
            "load_watts": self.load_watts,
            "daily_usage_hours": self.daily_usage_hours,
            "simulation_days": self.simulation_days,
            "location": self.location,
            "avg_sun_hours": self.avg_sun_hours,
            "summary": json.loads(self.summary_json) if self.summary_json else None,
            "recommendations": json.loads(self.recommendations_json) if self.recommendations_json else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }
