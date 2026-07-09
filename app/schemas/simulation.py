"""Pydantic schemas for Solar System Simulation Engine."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SimulationStatus(str, Enum):
    """Simulation status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EventType(str, Enum):
    """Event type enum."""
    WARNING = "warning"
    DAMAGE = "damage"
    FAILURE = "failure"
    INFO = "info"
    MILESTONE = "milestone"


class Severity(str, Enum):
    """Event severity enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SimulationInput(BaseModel):
    """Input model for solar system simulation."""
    battery_id: int = Field(..., description="Database ID of the battery product")
    inverter_id: int = Field(..., description="Database ID of the inverter product")
    panel_id: int = Field(..., description="Database ID of the solar panel product")
    charge_controller_id: int = Field(..., description="Database ID of the charge controller product")
    load_watts: float = Field(..., gt=0, description="Average load in watts")
    daily_usage_hours: float = Field(..., gt=0, le=24, description="Hours of daily load usage")
    simulation_days: int = Field(..., gt=0, le=36500, description="Number of days to simulate")
    location: Optional[str] = Field("default", description="Location for solar irradiance estimation")
    avg_sun_hours: Optional[float] = Field(5.0, gt=0, le=15, description="Average sun hours per day")
    
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "battery_id": 1,
                "inverter_id": 2,
                "panel_id": 3,
                "charge_controller_id": 4,
                "load_watts": 2500,
                "daily_usage_hours": 10,
                "simulation_days": 3650,
                "location": "default",
                "avg_sun_hours": 5.0
            }
        }
    )


class BatterySpec(BaseModel):
    """Battery specifications model."""
    voltage: float = Field(..., description="Nominal voltage in volts")
    capacity_ah: float = Field(..., description="Capacity in amp-hours")
    max_discharge_current: Optional[float] = Field(None, description="Max discharge current in amps")
    max_charge_current: Optional[float] = Field(None, description="Max charge current in amps")
    cycle_life: Optional[int] = Field(None, description="Expected cycle life at 80% DoD")
    round_trip_efficiency: Optional[float] = Field(0.85, description="Round-trip efficiency (0-1)")
    dod_max_safe: Optional[float] = Field(0.80, description="Maximum safe depth of discharge (0-1)")
    degradation_rate: Optional[float] = Field(0.00002, description="Base degradation rate per day")
    battery_type: Optional[str] = Field("lithium", description="Battery chemistry type")


class InverterSpec(BaseModel):
    """Inverter specifications model."""
    rated_power: float = Field(..., description="Rated continuous power in watts")
    battery_voltage_range_min: Optional[float] = Field(None, description="Min battery voltage")
    battery_voltage_range_max: Optional[float] = Field(None, description="Max battery voltage")
    surge_power: Optional[float] = Field(None, description="Surge power handling in watts")
    efficiency: Optional[float] = Field(0.95, description="Inversion efficiency (0-1)")
    overload_duration_max: Optional[float] = Field(60, description="Max overload duration in seconds")


class PanelSpec(BaseModel):
    """Solar panel specifications model."""
    wattage: float = Field(..., description="Panel wattage in watts")
    Voc: Optional[float] = Field(None, description="Open circuit voltage")
    Isc: Optional[float] = Field(None, description="Short circuit current")
    Vmp: Optional[float] = Field(None, description="Maximum power voltage")
    Imp: Optional[float] = Field(None, description="Maximum power current")
    panel_count: Optional[int] = Field(1, description="Number of panels")


class ChargeControllerSpec(BaseModel):
    """Charge controller specifications model."""
    max_input_voltage: Optional[float] = Field(None, description="Maximum input voltage")
    rated_current: Optional[float] = Field(None, description="Rated current in amps")
    efficiency: Optional[float] = Field(0.95, description="Charging efficiency (0-1)")
    max_charge_current: Optional[float] = Field(None, description="Maximum charge current")


class ComponentSpecs(BaseModel):
    """Combined component specifications."""
    battery: BatterySpec
    inverter: InverterSpec
    panel: PanelSpec
    charge_controller: ChargeControllerSpec


class SimulationEvent(BaseModel):
    """Simulation event log entry."""
    day: int = Field(..., description="Day of the event")
    type: EventType = Field(..., description="Type of event")
    severity: Severity = Field(..., description="Event severity")
    message: str = Field(..., description="Event description")
    component: str = Field(..., description="Affected component")
    details: Optional[dict] = Field(None, description="Additional event details")


class TimelineEntry(BaseModel):
    """Daily simulation timeline entry."""
    day: int = Field(..., description="Day number")
    date: str = Field(..., description="Simulated date")
    battery_soc: float = Field(..., description="Battery state of charge (0-1)")
    battery_health: float = Field(..., description="Battery health percentage (0-100)")
    daily_production_kwh: float = Field(..., description="Daily solar production in kWh")
    daily_consumption_kwh: float = Field(..., description="Daily load consumption in kWh")
    cycle_count: int = Field(..., description="Battery cycle count")
    inverter_load_percent: float = Field(..., description="Inverter load percentage")
    events: list[SimulationEvent] = Field(default_factory=list, description="Events on this day")


class Recommendation(BaseModel):
    """System recommendation."""
    category: str = Field(..., description="Recommendation category")
    priority: Severity = Field(..., description="Recommendation priority")
    title: str = Field(..., description="Short recommendation title")
    description: str = Field(..., description="Detailed recommendation description")
    component: Optional[str] = Field(None, description="Affected component")
    expected_improvement: Optional[str] = Field(None, description="Expected improvement from applying recommendation")


class SimulationSummary(BaseModel):
    """Simulation summary statistics."""
    battery_health_final: float = Field(..., description="Final battery health percentage")
    total_energy_produced_kwh: float = Field(..., description="Total energy produced in kWh")
    total_energy_consumed_kwh: float = Field(..., description="Total energy consumed in kWh")
    total_energy_lost_kwh: float = Field(..., description="Total energy lost in kWh")
    system_failures: int = Field(..., description="Total system failures")
    warnings: int = Field(..., description="Total warnings generated")
    cycle_count_total: int = Field(..., description="Total battery cycles")
    avg_daily_production_kwh: float = Field(..., description="Average daily production in kWh")
    avg_daily_consumption_kwh: float = Field(..., description="Average daily consumption in kWh")
    system_balance_percent: float = Field(..., description="Energy balance percentage")
    projected_battery_lifespan_years: float = Field(..., description="Projected battery lifespan in years")
    first_failure_day: Optional[int] = Field(None, description="Day of first system failure")
    max_inverter_load_percent: float = Field(..., description="Maximum inverter load percentage")


class SimulationOutput(BaseModel):
    """Output model for simulation results."""
    id: Optional[int] = Field(None, description="Simulation ID if saved")
    status: SimulationStatus = Field(..., description="Simulation status")
    input: SimulationInput = Field(..., description="Simulation input parameters")
    specs: ComponentSpecs = Field(..., description="Component specifications used")
    summary: SimulationSummary = Field(..., description="Simulation summary")
    timeline: list[TimelineEntry] = Field(default_factory=list, description="Daily timeline")
    events: list[SimulationEvent] = Field(default_factory=list, description="All events")
    recommendations: list[Recommendation] = Field(default_factory=list, description="System recommendations")
    created_at: Optional[datetime] = Field(None, description="Simulation creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Simulation completion timestamp")
    duration_ms: Optional[int] = Field(None, description="Simulation duration in milliseconds")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "status": "completed",
                "summary": {
                    "battery_health_final": 62.5,
                    "total_energy_produced_kwh": 18250.0,
                    "total_energy_consumed_kwh": 9125.0,
                    "total_energy_lost_kwh": 4562.5,
                    "system_failures": 3,
                    "warnings": 12,
                    "cycle_count_total": 2500,
                    "avg_daily_production_kwh": 5.0,
                    "avg_daily_consumption_kwh": 2.5,
                    "system_balance_percent": 100.0,
                    "projected_battery_lifespan_years": 8.5,
                    "first_failure_day": 365,
                    "max_inverter_load_percent": 95.0
                },
                "events": [],
                "recommendations": []
            }
        }
    )


class SimulationHistory(BaseModel):
    """Simulation history item."""
    id: int
    status: SimulationStatus
    input: SimulationInput
    summary: SimulationSummary
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class SimulationHistoryList(BaseModel):
    """Paginated simulation history list."""
    items: list[SimulationHistory]
    total: int
    page: int
    page_size: int
    pages: int


class ValidationError(BaseModel):
    """Validation error detail."""
    field: str = Field(..., description="Field with validation error")
    message: str = Field(..., description="Error message")
    suggestion: Optional[str] = Field(None, description="Suggestion to fix the error")


class SystemValidationResult(BaseModel):
    """Result of system compatibility validation."""
    valid: bool = Field(..., description="Whether the system is valid")
    errors: list[ValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
