"""
Solar System Simulation Engine.

Simulates realistic solar installation behavior over time, including:
- Battery degradation
- Overload damage
- Inverter stress/failure
- Charge controller limits
- System imbalance effects
"""
import math
import logging
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

import numpy as np

from app.schemas.simulation import (
    SimulationInput,
    SimulationOutput,
    SimulationSummary,
    SimulationStatus,
    ComponentSpecs,
    TimelineEntry,
    Recommendation,
    Severity,
    EventType,
    SimulationEvent,
)
from app.services.event_system import EventLogger, Event
from app.services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)


# Default sun hours by location (rough estimates)
LOCATION_SUN_HOURS = {
    "default": 5.0,
    "arizona": 6.5,
    "california": 5.5,
    "florida": 5.0,
    "texas": 5.5,
    "new_york": 4.0,
    "alaska": 3.0,
    "washington": 3.5,
    "nevada": 6.0,
    "colorado": 5.5,
    "michigan": 4.0,
    "alabama": 4.5,
    "georgia": 4.5,
    "oregon": 4.0,
}


@dataclass
class BatteryState:
    """Battery simulation state."""
    soc: float = 1.0  # State of Charge (0-1)
    health: float = 100.0  # Health percentage (0-100)
    cycle_count: int = 0
    capacity_ah_original: float = 0.0
    capacity_ah_current: float = 0.0
    dod_today: float = 0.0
    charge_cycles_day: int = 0
    last_soc: float = 1.0


@dataclass
class InverterState:
    """Inverter simulation state."""
    load_percent: float = 0.0
    max_load_percent: float = 0.0
    overload_seconds: float = 0.0
    failed: bool = False


@dataclass
class SystemState:
    """Combined system simulation state."""
    battery: BatteryState
    inverter: InverterState
    daily_production_kwh: float = 0.0
    daily_consumption_kwh: float = 0.0
    total_production_kwh: float = 0.0
    total_consumption_kwh: float = 0.0
    total_lost_kwh: float = 0.0
    first_failure_day: Optional[int] = None


class BatteryModel:
    """Battery degradation and behavior model."""

    def __init__(self, specs: ComponentSpecs, event_logger: EventLogger):
        self.specs = specs.battery
        self.state = BatteryState()
        self.state.capacity_ah_original = specs.battery.capacity_ah
        self.state.capacity_ah_current = specs.battery.capacity_ah
        self.event_logger = event_logger

    def reset(self):
        """Reset battery to initial state."""
        self.state = BatteryState()
        self.state.capacity_ah_original = self.specs.capacity_ah
        self.state.capacity_ah_current = self.specs.capacity_ah

    @property
    def capacity_wh(self) -> float:
        """Get current capacity in Wh."""
        return self.state.capacity_ah_current * self.specs.voltage

    @property
    def original_capacity_wh(self) -> float:
        """Get original capacity in Wh."""
        return self.state.capacity_ah_original * self.specs.voltage

    def simulate_day(
        self,
        day: int,
        energy_to_battery_kwh: float,
        energy_from_battery_kwh: float,
        discharge_current: float,
        charge_current: float,
        sun_hours: float
    ) -> list[Event]:
        """Simulate one day of battery operation."""
        events = []

        # Track daily DoD
        dod_yesterday = self.state.dod_today
        self.state.dod_today = 0.0

        # Calculate energy changes
        energy_to_wh = energy_to_battery_kwh * 1000
        energy_from_wh = energy_from_battery_kwh * 1000

        # Apply round-trip efficiency to charging
        efficiency = self.specs.round_trip_efficiency
        energy_to_wh *= efficiency

        # Update SOC
        soc_change = (energy_to_wh - energy_from_wh) / self.capacity_wh if self.capacity_wh > 0 else 0
        self.state.soc = max(0, min(1, self.state.soc + soc_change))

        # Calculate DoD for this discharge
        dod_today = (1 - self.state.soc) if self.state.soc < 1 else 0
        self.state.dod_today = max(dod_yesterday, dod_today)

        # Check for deep discharge
        if self.state.soc < 0.2:
            self.event_logger.log_warning(
                day=day,
                message=f"Battery critically low SOC: {self.state.soc * 100:.1f}%",
                component="battery",
                severity=Severity.HIGH,
                details={"soc": self.state.soc, "dod": self.state.dod_today}
            )

        # Check for over-discharge
        max_safe_dod = self.specs.dod_max_safe
        if self.state.dod_today > max_safe_dod:
            damage = 0.02 * (self.state.dod_today - max_safe_dod)  # 2% extra degradation per 10% over DoD
            self.state.health -= damage * 100
            self.event_logger.log_damage(
                day=day,
                message=f"Battery exceeded safe DoD ({self.state.dod_today * 100:.1f}% > {max_safe_dod * 100:.0f}%)",
                component="battery",
                severity=Severity.HIGH,
                details={"dod": self.state.dod_today, "max_safe": max_safe_dod, "damage": damage}
            )

        # Check for overcurrent damage
        max_discharge = self.specs.max_discharge_current
        if max_discharge and discharge_current > max_discharge:
            overcurrent_factor = discharge_current / max_discharge
            damage = 0.05 * (overcurrent_factor - 1)  # 5% extra degradation per 20% overcurrent
            self.state.health -= damage * 100
            self.event_logger.log_damage(
                day=day,
                message=f"Battery overcurrent: {discharge_current:.1f}A > max {max_discharge:.1f}A",
                component="battery",
                severity=Severity.MEDIUM,
                details={"discharge_current": discharge_current, "max_discharge": max_discharge, "damage": damage}
            )

        # Check for overcharge
        max_charge = self.specs.max_charge_current
        if max_charge and charge_current > max_charge:
            overcurrent_factor = charge_current / max_charge
            damage = 0.03 * (overcurrent_factor - 1)
            self.state.health -= damage * 100
            self.event_logger.log_warning(
                day=day,
                message=f"Battery overcharge current: {charge_current:.1f}A > max {max_charge:.1f}A",
                component="battery",
                severity=Severity.MEDIUM,
                details={"charge_current": charge_current, "max_charge": max_charge}
            )

        # Track cycles
        if dod_today > 0.1:  # Significant discharge counts as partial cycle
            self.state.cycle_count += 1
            self.state.charge_cycles_day = 1

        # Apply base degradation (calendar aging + cycle aging)
        # Base degradation: ~2% per year from calendar aging + cycle aging
        daily_base_degradation = 0.00002  # ~0.73% per year
        cycle_degradation = 0.00001 * (self.state.dod_today / 0.8) if self.state.dod_today > 0 else 0
        self.state.health -= (daily_base_degradation + cycle_degradation) * 100

        # Update current capacity based on health
        health_factor = self.state.health / 100
        self.state.capacity_ah_current = self.state.capacity_ah_original * health_factor

        # Clamp health
        self.state.health = max(0, min(100, self.state.health))

        # Check for battery failure
        if self.state.health <= 0:
            self.event_logger.log_failure(
                day=day,
                message="Battery has failed - health reached 0%",
                component="battery",
                details={"final_health": self.state.health, "cycle_count": self.state.cycle_count}
            )

        # Log yearly milestones
        if day > 0 and day % 365 == 0:
            self.event_logger.log_milestone(
                day=day,
                message=f"Battery at year {day // 365}: Health={self.state.health:.1f}%, Cycles={self.state.cycle_count}",
                component="battery"
            )

        return events


class InverterModel:
    """Inverter stress and failure model."""

    def __init__(self, specs: ComponentSpecs, event_logger: EventLogger):
        self.specs = specs.inverter
        self.state = InverterState()
        self.event_logger = event_logger

    def reset(self):
        """Reset inverter to initial state."""
        self.state = InverterState()

    def simulate_day(self, day: int, load_watts: float) -> list[Event]:
        """Simulate one day of inverter operation."""
        events = []

        # Calculate load percentage
        load_percent = (load_watts / self.specs.rated_power) * 100 if self.specs.rated_power > 0 else 0
        self.state.load_percent = load_percent

        # Track max load
        if load_percent > self.state.max_load_percent:
            self.state.max_load_percent = load_percent

        # Check for overload
        surge_power = self.specs.surge_power or self.specs.rated_power * 1.5
        if load_watts > surge_power:
            # Surge overload - calculate equivalent overload time
            overload_factor = load_watts / surge_power
            self.state.overload_seconds += 60 / 24 * overload_factor  # Approximate daily accumulation

            if self.state.overload_seconds > self.specs.overload_duration_max:
                self.event_logger.log_failure(
                    day=day,
                    message=f"Inverter surge failure: Load {load_watts:.0f}W exceeded surge capacity {surge_power:.0f}W",
                    component="inverter",
                    details={"load_watts": load_watts, "surge_power": surge_power}
                )
                self.state.failed = True
            else:
                self.event_logger.log_warning(
                    day=day,
                    message=f"Inverter surge load: {load_watts:.0f}W (surge capacity: {surge_power:.0f}W)",
                    component="inverter",
                    severity=Severity.MEDIUM
                )

        elif load_watts > self.specs.rated_power:
            # Continuous overload
            self.state.overload_seconds += 60 / 24  # Add 1 minute equivalent per day
            self.event_logger.log_warning(
                day=day,
                message=f"Inverter overloaded: {load_watts:.0f}W > rated {self.specs.rated_power:.0f}W",
                component="inverter",
                severity=Severity.LOW,
                details={"load_watts": load_watts, "rated_power": self.specs.rated_power}
            )

        # Check for efficiency impact at high loads
        if load_percent > 90:
            efficiency_loss = (load_percent - 90) * 0.001  # Minor efficiency loss
            if efficiency_loss > 0.01:  # Only log if significant
                self.event_logger.log_info(
                    day=day,
                    message=f"High inverter load affecting efficiency: {load_percent:.1f}%",
                    component="inverter",
                    details={"load_percent": load_percent, "efficiency_loss": efficiency_loss}
                )

        return events


class ChargeControllerModel:
    """Charge controller efficiency and limits model."""

    def __init__(self, specs: ComponentSpecs, event_logger: EventLogger):
        self.specs = specs.charge_controller
        self.event_logger = event_logger
        self.total_input_voltage = 0.0
        self.peak_input_voltage = 0.0

    def reset(self):
        """Reset charge controller to initial state."""
        self.total_input_voltage = 0.0
        self.peak_input_voltage = 0.0

    def simulate_day(
        self,
        day: int,
        panel_voltage: float,
        panel_current: float,
        energy_to_battery_kwh: float
    ) -> tuple[float, list[Event]]:
        """
        Simulate one day of charge controller operation.
        
        Returns: Tuple of (efficiency factor, events)
        """
        events = []
        efficiency = self.specs.efficiency or 0.95

        # Track peak voltage
        if panel_voltage > self.peak_input_voltage:
            self.peak_input_voltage = panel_voltage

        # Check max input voltage
        max_voltage = self.specs.max_input_voltage
        if max_voltage and panel_voltage > max_voltage:
            # Voltage clipping - potential damage
            voltage_excess = (panel_voltage - max_voltage) / max_voltage
            self.event_logger.log_warning(
                day=day,
                message=f"Panel voltage ({panel_voltage:.1f}V) exceeds controller max ({max_voltage:.1f}V)",
                component="charge_controller",
                severity=Severity.HIGH,
                details={"panel_voltage": panel_voltage, "max_voltage": max_voltage}
            )
            # Apply efficiency penalty
            efficiency *= (1 - voltage_excess * 0.5)

        # Check rated current
        rated_current = self.specs.rated_current
        if rated_current and panel_current > rated_current:
            self.event_logger.log_warning(
                day=day,
                message=f"Panel current ({panel_current:.1f}A) exceeds controller rating ({rated_current:.1f}A)",
                component="charge_controller",
                severity=Severity.LOW,
                details={"panel_current": panel_current, "rated_current": rated_current}
            )
            # Current limiting reduces available power
            limiting_factor = rated_current / panel_current if panel_current > 0 else 1
            efficiency *= limiting_factor

        # Check max charge current
        max_charge = self.specs.max_charge_current
        if max_charge:
            battery_voltage = 48  # Assumed from specs
            charge_power = energy_to_battery_kwh * 1000 / 24  # Average charge power
            charge_current = charge_power / battery_voltage if battery_voltage > 0 else 0
            
            if charge_current > max_charge:
                self.event_logger.log_warning(
                    day=day,
                    message=f"Battery charge current ({charge_current:.1f}A) exceeds controller max ({max_charge:.1f}A)",
                    component="charge_controller",
                    severity=Severity.MEDIUM
                )

        return efficiency, events


class SolarProductionModel:
    """Solar panel production model."""

    def __init__(self, specs: ComponentSpecs):
        self.specs = specs.panel
        self.panel_count = specs.panel.panel_count or 1

    def calculate_daily_production(self, sun_hours: float, efficiency_factor: float = 0.8) -> float:
        """Calculate daily solar production in kWh."""
        # Panel wattage * sun hours * panel count * system efficiency
        total_wattage = self.specs.wattage * self.panel_count
        production_wh = total_wattage * sun_hours * efficiency_factor
        return production_wh / 1000  # Convert to kWh


class SolarSimulationEngine:
    """
    Main simulation engine for solar system behavior.

    Coordinates battery, inverter, charge controller, and solar production models
    to simulate realistic system behavior over time.
    """

    def __init__(
        self,
        specs: ComponentSpecs,
        input_params: SimulationInput
    ):
        """Initialize the simulation engine."""
        self.specs = specs
        self.input = input_params
        self.event_logger = EventLogger()
        
        # Initialize component models
        self.battery_model = BatteryModel(specs, self.event_logger)
        self.inverter_model = InverterModel(specs, self.event_logger)
        self.charge_controller_model = ChargeControllerModel(specs, self.event_logger)
        self.solar_production_model = SolarProductionModel(specs)
        
        # Recommendation engine
        self.recommendation_engine = RecommendationEngine(specs, input_params)

    def _get_sun_hours(self, day: int) -> float:
        """Get sun hours for a given day, with seasonal variation."""
        base_sun_hours = LOCATION_SUN_HOURS.get(
            self.input.location.lower(), 
            self.input.avg_sun_hours
        )
        
        # Add seasonal variation (simplified sine wave)
        day_of_year = day % 365
        seasonal_factor = math.sin(2 * math.pi * (day_of_year - 80) / 365)
        sun_hours = base_sun_hours * (1 + 0.15 * seasonal_factor)
        
        return max(1.0, min(10.0, sun_hours))  # Clamp between 1 and 10 hours

    def _simulate_day(self, day: int) -> TimelineEntry:
        """Simulate one day of system operation."""
        # Get sun hours for this day
        sun_hours = self._get_sun_hours(day)
        
        # Calculate solar production
        daily_production_kwh = self.solar_production_model.calculate_daily_production(sun_hours)
        
        # Calculate load consumption
        daily_consumption_kwh = (self.input.load_watts * self.input.daily_usage_hours) / 1000
        
        # Energy available after charge controller efficiency
        cc_efficiency, _ = self.charge_controller_model.simulate_day(
            day,
            panel_voltage=self.specs.panel.Voc or 40,
            panel_current=self.specs.panel.Isc or 10,
            energy_to_battery_kwh=daily_production_kwh
        )
        energy_after_cc = daily_production_kwh * cc_efficiency
        
        # Calculate energy balance
        energy_balance = energy_after_cc - daily_consumption_kwh
        
        # Determine energy flow
        if energy_balance >= 0:
            # Surplus: charge battery, then dump excess
            energy_to_battery = min(energy_balance, self.battery_model.capacity_wh / 1000 * (1 - self.battery_model.state.soc))
            energy_to_battery *= self.specs.battery.round_trip_efficiency
            energy_dump = energy_balance - energy_to_battery
            energy_from_battery = 0
        else:
            # Deficit: discharge battery
            energy_from_battery = abs(energy_balance)
            energy_to_battery = 0
            energy_dump = 0
        
        # Calculate currents
        battery_voltage = self.specs.battery.voltage
        discharge_current = (energy_from_battery * 1000) / battery_voltage / self.input.daily_usage_hours if battery_voltage > 0 else 0
        charge_current = (energy_to_battery * 1000) / battery_voltage / sun_hours if battery_voltage > 0 else 0
        
        # Inverter simulation
        self.inverter_model.simulate_day(day, self.input.load_watts)
        
        # Battery simulation
        self.battery_model.simulate_day(
            day,
            energy_to_battery,
            energy_from_battery,
            discharge_current,
            charge_current,
            sun_hours
        )
        
        # Update system totals
        self.state.total_production_kwh += energy_after_cc
        self.state.total_consumption_kwh += daily_consumption_kwh
        self.state.total_lost_kwh += energy_dump + daily_consumption_kwh * (1 - self.specs.inverter.efficiency)
        self.state.daily_production_kwh = energy_after_cc
        self.state.daily_consumption_kwh = daily_consumption_kwh
        
        # Check for system failure
        if self.battery_model.state.health <= 0 or self.inverter_model.state.failed:
            if self.state.first_failure_day is None:
                self.state.first_failure_day = day
                self.event_logger.log_failure(
                    day=day,
                    message="System has failed - primary components no longer functional",
                    component="system"
                )

        # Get events for this day
        day_events = self.event_logger.get_events_by_day(day)
        
        # Create timeline entry
        simulated_date = datetime.now() - timedelta(days=self.input.simulation_days - day)
        timeline_entry = TimelineEntry(
            day=day,
            date=simulated_date.strftime("%Y-%m-%d"),
            battery_soc=round(self.battery_model.state.soc, 4),
            battery_health=round(self.battery_model.state.health, 2),
            daily_production_kwh=round(daily_production_kwh, 3),
            daily_consumption_kwh=round(daily_consumption_kwh, 3),
            cycle_count=self.battery_model.state.cycle_count,
            inverter_load_percent=round(self.inverter_model.state.load_percent, 2),
            events=[
                SimulationEvent(
                    day=e.day,
                    type=e.event_type,
                    severity=e.severity,
                    message=e.message,
                    component=e.component,
                    details=e.details if e.details else None
                ) for e in day_events
            ]
        )
        
        return timeline_entry

    def run(self) -> SimulationOutput:
        """Run the full simulation."""
        # Initialize state
        self.state = SystemState(
            battery=BatteryState(
                capacity_ah_original=self.specs.battery.capacity_ah,
                capacity_ah_current=self.specs.battery.capacity_ah
            ),
            inverter=InverterState()
        )
        
        # Reset all models
        self.battery_model.reset()
        self.inverter_model.reset()
        self.charge_controller_model.reset()
        self.event_logger.clear()
        
        timeline = []
        start_time = datetime.now()
        
        # Run daily simulation
        for day in range(1, self.input.simulation_days + 1):
            timeline_entry = self._simulate_day(day)
            timeline.append(timeline_entry)
            
            # Early termination if system fails
            if self.battery_model.state.health <= 0 or self.inverter_model.state.failed:
                if day < self.input.simulation_days:
                    # Pad timeline to full length with last state
                    remaining_days = self.input.simulation_days - day
                    for remaining_day in range(1, remaining_days + 1):
                        last_entry = timeline[-1]
                        timeline.append(TimelineEntry(
                            day=day + remaining_day,
                            date=last_entry.date,
                            battery_soc=last_entry.battery_soc,
                            battery_health=0.0,
                            daily_production_kwh=0.0,
                            daily_consumption_kwh=last_entry.daily_consumption_kwh,
                            cycle_count=last_entry.cycle_count,
                            inverter_load_percent=0.0,
                            events=[]
                        ))
                break
        
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Generate recommendations
        recommendations = self.recommendation_engine.generate(timeline, self.event_logger)
        
        # Calculate summary
        event_counts = self.event_logger.get_event_counts()
        summary = SimulationSummary(
            battery_health_final=round(self.battery_model.state.health, 2),
            total_energy_produced_kwh=round(self.state.total_production_kwh, 2),
            total_energy_consumed_kwh=round(self.state.total_consumption_kwh, 2),
            total_energy_lost_kwh=round(self.state.total_lost_kwh, 2),
            system_failures=event_counts.get(EventType.FAILURE, 0),
            warnings=event_counts.get(EventType.WARNING, 0),
            cycle_count_total=self.battery_model.state.cycle_count,
            avg_daily_production_kwh=round(self.state.total_production_kwh / max(1, len(timeline)), 3),
            avg_daily_consumption_kwh=round(self.state.total_consumption_kwh / max(1, len(timeline)), 3),
            system_balance_percent=round(
                (self.state.total_production_kwh / max(1, self.state.total_consumption_kwh)) * 100, 2
            ),
            projected_battery_lifespan_years=round(
                self.battery_model.state.health / max(0.73, 100 / 10), 2  # ~0.73% per year base degradation
            ),
            first_failure_day=self.state.first_failure_day,
            max_inverter_load_percent=round(self.inverter_model.state.max_load_percent, 2)
        )
        
        return SimulationOutput(
            status=SimulationStatus.COMPLETED,
            input=self.input,
            specs=self.specs,
            summary=summary,
            timeline=timeline,
            events=self.event_logger.to_simulation_events(),
            recommendations=recommendations,
            created_at=start_time,
            completed_at=end_time,
            duration_ms=duration_ms
        )
