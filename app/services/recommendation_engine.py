"""Recommendation Engine for Solar System Simulation."""
from typing import Optional

from app.schemas.simulation import (
    SimulationInput,
    SimulationOutput,
    ComponentSpecs,
    Recommendation,
    Severity,
    TimelineEntry,
)
from app.services.event_system import EventLogger, EventType


class RecommendationEngine:
    """Generates recommendations based on simulation results."""

    def __init__(self, specs: ComponentSpecs, input_params: SimulationInput):
        """Initialize the recommendation engine."""
        self.specs = specs
        self.input = input_params

    def generate(
        self,
        timeline: list[TimelineEntry],
        event_logger: EventLogger
    ) -> list[Recommendation]:
        """Generate recommendations based on simulation results."""
        recommendations = []

        if not timeline:
            return recommendations

        final_entry = timeline[-1]
        first_365_days = timeline[:365] if len(timeline) >= 365 else timeline

        # Analyze battery health
        recommendations.extend(self._analyze_battery_health(final_entry, first_365_days, event_logger))

        # Analyze inverter load
        recommendations.extend(self._analyze_inverter_load(final_entry))

        # Analyze system balance
        recommendations.extend(self._analyze_system_balance(final_entry))

        # Analyze charge controller
        recommendations.extend(self._analyze_charge_controller())

        # Analyze load patterns
        recommendations.extend(self._analyze_load_patterns())

        # Sort by priority (critical first)
        priority_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 99))

        return recommendations

    def _analyze_battery_health(
        self,
        final_entry: TimelineEntry,
        first_year: list[TimelineEntry],
        event_logger: EventLogger
    ) -> list[Recommendation]:
        """Analyze battery health and generate recommendations."""
        recommendations = []

        battery_health = final_entry.battery_health
        cycle_count = final_entry.cycle_count

        # Battery degradation too fast
        if battery_health < 80:
            yearly_degradation = 100 - battery_health
            if yearly_degradation > 5:
                recommendations.append(Recommendation(
                    category="battery",
                    priority=Severity.HIGH,
                    title="Rapid Battery Degradation Detected",
                    description=(
                        f"Battery health has degraded to {battery_health:.1f}% "
                        f"({yearly_degradation:.1f}% per year). This exceeds normal degradation rates. "
                        f"Common causes: excessive depth of discharge, overcurrent, or poor charging settings."
                    ),
                    component="battery",
                    expected_improvement="Reduce DoD to 50% or less, ensure proper charge controller settings"
                ))

        # High cycle count warning
        if cycle_count > 1000:
            recommendations.append(Recommendation(
                category="battery",
                priority=Severity.MEDIUM,
                title="High Battery Cycle Count",
                description=(
                    f"Battery has completed {cycle_count} cycles in the simulation period. "
                    f"Consider reducing daily depth of discharge to extend battery lifespan."
                ),
                component="battery",
                expected_improvement="Reduce load or increase battery capacity to lower daily DoD"
            ))

        # Battery too small for load
        battery_capacity_wh = self.specs.battery.capacity_ah * self.specs.battery.voltage
        daily_consumption_wh = self.input.load_watts * self.input.daily_usage_hours
        dod_required = daily_consumption_wh / battery_capacity_wh if battery_capacity_wh > 0 else 0

        if dod_required > 0.5:
            recommendations.append(Recommendation(
                category="battery",
                priority=Severity.HIGH,
                title="Undersized Battery for Load",
                description=(
                    f"Daily energy requirement ({daily_consumption_wh:.0f}Wh) exceeds 50% of battery capacity "
                    f"({battery_capacity_wh:.0f}Wh). This causes rapid degradation and may lead to system failure."
                ),
                component="battery",
                expected_improvement=f"Increase battery capacity to at least {daily_consumption_wh * 2:.0f}Wh"
            ))

        # Check for damage events
        damage_events = event_logger.get_events_by_type(EventType.DAMAGE)
        battery_damages = [e for e in damage_events if e.component == "battery"]
        if len(battery_damages) > 10:
            recommendations.append(Recommendation(
                category="battery",
                priority=Severity.HIGH,
                title="Frequent Battery Damage Events",
                description=(
                    f"{len(battery_damages)} battery damage events detected. "
                    f"This indicates sustained stress on the battery beyond safe operating parameters."
                ),
                component="battery",
                expected_improvement="Review and adjust charge controller settings, reduce load"
            ))

        return recommendations

    def _analyze_inverter_load(self, final_entry: TimelineEntry) -> list[Recommendation]:
        """Analyze inverter load and generate recommendations."""
        recommendations = []

        max_load_percent = final_entry.inverter_load_percent

        # Inverter overloaded
        if max_load_percent > 100:
            oversizing_factor = max_load_percent / 100
            recommendations.append(Recommendation(
                category="inverter",
                priority=Severity.CRITICAL,
                title="Inverter Severely Overloaded",
                description=(
                    f"Inverter load reached {max_load_percent:.0f}% of rated capacity. "
                    f"This causes overheating, efficiency loss, and potential failure."
                ),
                component="inverter",
                expected_improvement=f"Upgrade to inverter with at least {self.input.load_watts * 1.25:.0f}W rated capacity"
            ))

        elif max_load_percent > 85:
            recommendations.append(Recommendation(
                category="inverter",
                priority=Severity.MEDIUM,
                title="Inverter Running Near Capacity",
                description=(
                    f"Inverter load reached {max_load_percent:.0f}% of rated capacity. "
                    f"Consider upgrading for better efficiency and longevity."
                ),
                component="inverter",
                expected_improvement=f"Upgrade to inverter with at least {self.input.load_watts * 1.2:.0f}W rated capacity"
            ))

        return recommendations

    def _analyze_system_balance(self, final_entry: TimelineEntry) -> list[Recommendation]:
        """Analyze overall system energy balance."""
        recommendations = []

        # Check if production is insufficient
        avg_production = final_entry.daily_production_kwh
        avg_consumption = final_entry.daily_consumption_kwh

        if avg_consumption > avg_production * 0.9:
            recommendations.append(Recommendation(
                category="system",
                priority=Severity.HIGH,
                title="Insufficient Solar Production",
                description=(
                    f"Average daily production ({avg_production:.2f}kWh) barely meets or exceeds "
                    f"daily consumption ({avg_consumption:.2f}kWh). System is barely sustainable."
                ),
                component="system",
                expected_improvement="Add more panels or reduce daily usage"
            ))

        # Check for energy surplus (potential overproduction)
        if avg_production > avg_consumption * 2:
            panel_count = self.specs.panel.panel_count or 1
            current_panel_watts = self.specs.panel.wattage * panel_count
            recommendations.append(Recommendation(
                category="system",
                priority=Severity.LOW,
                title="Excess Solar Production",
                description=(
                    f"System produces {avg_production:.2f}kWh daily but only uses {avg_consumption:.2f}kWh. "
                    f"Consider reducing panel count or adding battery storage."
                ),
                component="panel",
                expected_improvement="Consider reducing panels or adding battery storage for night usage"
            ))

        return recommendations

    def _analyze_charge_controller(self) -> list[Recommendation]:
        """Analyze charge controller configuration."""
        recommendations = []

        cc_current = self.specs.charge_controller.rated_current or 0
        bat_max_charge = self.specs.battery.max_charge_current or 0

        # Undersized charge controller
        if cc_current > 0 and bat_max_charge > 0:
            if cc_current < bat_max_charge * 0.5:
                recommendations.append(Recommendation(
                    category="charge_controller",
                    priority=Severity.MEDIUM,
                    title="Undersized Charge Controller",
                    description=(
                        f"Charge controller ({cc_current}A) may limit battery charging from "
                        f"panels designed for {bat_max_charge}A charge current."
                    ),
                    component="charge_controller",
                    expected_improvement=f"Upgrade to charge controller with at least {bat_max_charge:.0f}A rating"
                ))

        return recommendations

    def _analyze_load_patterns(self) -> list[Recommendation]:
        """Analyze load patterns and suggest improvements."""
        recommendations = []

        daily_usage = self.input.daily_usage_hours

        # Very high daily usage
        if daily_usage > 12:
            recommendations.append(Recommendation(
                category="load",
                priority=Severity.MEDIUM,
                title="Very High Daily Usage",
                description=(
                    f"System is designed for {daily_usage:.1f} hours of daily use. "
                    f"Consider spreading load or improving energy efficiency."
                ),
                component="load",
                expected_improvement="Reduce peak usage hours or improve appliance efficiency"
            ))

        return recommendations


def generate_system_sizing_recommendation(
    load_watts: float,
    daily_hours: float,
    sun_hours: float,
    battery_days_autonomy: int = 1
) -> dict:
    """
    Generate system sizing recommendations.
    
    This is a utility function that can be used independently of simulation.
    """
    daily_wh = load_watts * daily_hours
    panel_watts_needed = daily_wh / sun_hours / 0.8  # 80% efficiency factor
    battery_wh_needed = daily_wh * battery_days_autonomy / 0.5  # 50% DoD
    inverter_watts = load_watts * 1.25  # 25% overhead

    return {
        "panel_watts_needed": round(panel_watts_needed, 0),
        "battery_wh_needed": round(battery_wh_needed, 0),
        "inverter_watts_needed": round(inverter_watts, 0),
        "daily_energy_kwh": round(daily_wh / 1000, 2),
        "system_recommendations": []
    }
