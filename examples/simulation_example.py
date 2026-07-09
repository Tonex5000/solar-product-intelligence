"""
Example Solar System Simulation.

This script demonstrates how to use the Solar Simulation Engine
with hardcoded component specifications (simulating database specs).
"""
import json
import sys
sys.path.insert(0, '/workspace/project/solar-product-intelligence')

from app.schemas.simulation import (
    SimulationInput,
    ComponentSpecs,
    BatterySpec,
    InverterSpec,
    PanelSpec,
    ChargeControllerSpec,
)
from app.services.simulation_engine import SolarSimulationEngine
from app.services.recommendation_engine import generate_system_sizing_recommendation


def run_example_simulation():
    """Run an example simulation demonstrating system behavior."""
    
    # Define component specifications (normally loaded from database)
    specs = ComponentSpecs(
        battery=BatterySpec(
            voltage=48,
            capacity_ah=200,
            max_discharge_current=150,
            max_charge_current=100,
            cycle_life=4000,
            round_trip_efficiency=0.92,
            dod_max_safe=0.80,
            degradation_rate=0.00002,
            battery_type="lithium"
        ),
        inverter=InverterSpec(
            rated_power=5000,
            battery_voltage_range_min=40,
            battery_voltage_range_max=60,
            surge_power=7500,
            efficiency=0.95,
            overload_duration_max=60
        ),
        panel=PanelSpec(
            wattage=400,
            Voc=48,
            Isc=10,
            Vmp=40,
            Imp=10,
            panel_count=10
        ),
        charge_controller=ChargeControllerSpec(
            max_input_voltage=150,
            rated_current=60,
            efficiency=0.95,
            max_charge_current=100
        )
    )

    # Define simulation parameters
    simulation_input = SimulationInput(
        battery_id=1,
        inverter_id=2,
        panel_id=3,
        charge_controller_id=4,
        load_watts=2500,  # 2.5kW average load
        daily_usage_hours=10,  # 10 hours per day
        simulation_days=3650,  # 10 years
        location="california",
        avg_sun_hours=5.5
    )

    print("=" * 60)
    print("SOLAR SYSTEM SIMULATION ENGINE - EXAMPLE RUN")
    print("=" * 60)
    print()
    print("Component Specifications:")
    print(f"  Battery: {specs.battery.voltage}V, {specs.battery.capacity_ah}Ah")
    print(f"  Inverter: {specs.inverter.rated_power}W rated, {specs.inverter.surge_power}W surge")
    print(f"  Panels: {specs.panel.panel_count}x {specs.panel.wattage}W = {specs.panel.panel_count * specs.panel.wattage}W total")
    print(f"  Charge Controller: {specs.charge_controller.rated_current}A")
    print()
    print("Simulation Parameters:")
    print(f"  Load: {simulation_input.load_watts}W for {simulation_input.daily_usage_hours} hours/day")
    print(f"  Duration: {simulation_input.simulation_days} days ({simulation_input.simulation_days // 365} years)")
    print(f"  Location: {simulation_input.location} ({simulation_input.avg_sun_hours} sun hours/day)")
    print()
    print("Running simulation...")
    print()

    # Create and run simulation
    engine = SolarSimulationEngine(specs=specs, input_params=simulation_input)
    result = engine.run()

    # Print results
    print("=" * 60)
    print("SIMULATION RESULTS")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  Status: {result.status.value}")
    print(f"  Duration: {result.duration_ms}ms")
    print(f"  Final Battery Health: {result.summary.battery_health_final:.1f}%")
    print(f"  Total Cycles: {result.summary.cycle_count_total}")
    print(f"  System Failures: {result.summary.system_failures}")
    print(f"  Warnings: {result.summary.warnings}")
    print()
    print("Energy Summary:")
    print(f"  Total Produced: {result.summary.total_energy_produced_kwh:.2f} kWh")
    print(f"  Total Consumed: {result.summary.total_energy_consumed_kwh:.2f} kWh")
    print(f"  Total Lost: {result.summary.total_energy_lost_kwh:.2f} kWh")
    print(f"  Avg Daily Production: {result.summary.avg_daily_production_kwh:.2f} kWh")
    print(f"  Avg Daily Consumption: {result.summary.avg_daily_consumption_kwh:.2f} kWh")
    print(f"  System Balance: {result.summary.system_balance_percent:.1f}%")
    print()
    print(f"Projected Battery Lifespan: {result.summary.projected_battery_lifespan_years:.1f} years")
    print(f"First Failure Day: {result.summary.first_failure_day or 'None'}")
    print(f"Max Inverter Load: {result.summary.max_inverter_load_percent:.1f}%")
    print()

    # Print key events
    print("Key Events:")
    critical_events = [e for e in result.events if e.severity.value in ['critical', 'high']]
    for event in critical_events[:10]:
        print(f"  Day {event.day}: [{event.type.value.upper()}] {event.message}")
    if len(critical_events) > 10:
        print(f"  ... and {len(critical_events) - 10} more critical events")
    print()

    # Print recommendations
    print("Recommendations:")
    for rec in result.recommendations[:5]:
        print(f"  [{rec.priority.value.upper()}] {rec.title}")
        print(f"    {rec.description[:100]}...")
    print()

    # Sample timeline (first and last year)
    print("Sample Timeline (Year 1 vs Year 10):")
    if len(result.timeline) > 0:
        year1 = result.timeline[0]
        print(f"  Day 1: SOC={year1.battery_soc*100:.1f}%, Health={year1.battery_health:.1f}%, "
              f"Production={year1.daily_production_kwh:.2f}kWh, Consumption={year1.daily_consumption_kwh:.2f}kWh")
    
    if len(result.timeline) >= 365:
        year10 = result.timeline[364]
        print(f"  Day 365: SOC={year10.battery_soc*100:.1f}%, Health={year10.battery_health:.1f}%, "
              f"Production={year10.daily_production_kwh:.2f}kWh, Consumption={year10.daily_consumption_kwh:.2f}kWh")
    
    if len(result.timeline) >= 3650:
        year_end = result.timeline[-1]
        print(f"  Day 3650: SOC={year_end.battery_soc*100:.1f}%, Health={year_end.battery_health:.1f}%, "
              f"Production={year_end.daily_production_kwh:.2f}kWh")
    elif len(result.timeline) > 0:
        last_day = result.timeline[-1]
        print(f"  Day {last_day.day}: SOC={last_day.battery_soc*100:.1f}%, Health={last_day.battery_health:.1f}%")

    print()
    print("=" * 60)
    
    return result


def run_oversized_load_simulation():
    """Simulate an oversized load scenario that should cause damage."""
    
    print()
    print("=" * 60)
    print("OVERSIZED LOAD SCENARIO")
    print("=" * 60)
    print()
    
    # Same components but 50% higher load
    specs = ComponentSpecs(
        battery=BatterySpec(
            voltage=48,
            capacity_ah=200,
            max_discharge_current=150,
            cycle_life=4000,
            round_trip_efficiency=0.92,
            dod_max_safe=0.80,
            battery_type="lithium"
        ),
        inverter=InverterSpec(
            rated_power=5000,
            surge_power=7500,
            efficiency=0.95
        ),
        panel=PanelSpec(
            wattage=400,
            Voc=48,
            Isc=10,
            panel_count=10
        ),
        charge_controller=ChargeControllerSpec(
            rated_current=60,
            efficiency=0.95
        )
    )

    simulation_input = SimulationInput(
        battery_id=1,
        inverter_id=2,
        panel_id=3,
        charge_controller_id=4,
        load_watts=6000,  # 6kW - over inverter rating
        daily_usage_hours=8,
        simulation_days=365,  # 1 year
        location="arizona",
        avg_sun_hours=6.5
    )

    print("Configuration:")
    print(f"  Load: {simulation_input.load_watts}W (OVER INVERTER RATING!)")
    print(f"  Inverter: {specs.inverter.rated_power}W rated")
    print(f"  Duration: 1 year")
    print()
    print("Running simulation...")
    print()

    engine = SolarSimulationEngine(specs=specs, input_params=simulation_input)
    result = engine.run()

    print("Results:")
    print(f"  System Failures: {result.summary.system_failures}")
    print(f"  Warnings: {result.summary.warnings}")
    print(f"  Max Inverter Load: {result.summary.max_inverter_load_percent:.1f}%")
    print()
    print("Recommendations:")
    for rec in result.recommendations:
        if rec.category == "inverter":
            print(f"  [{rec.priority.value.upper()}] {rec.title}")
            print(f"    {rec.description}")

    return result


def run_sizing_calculator_example():
    """Show system sizing recommendations."""
    
    print()
    print("=" * 60)
    print("SYSTEM SIZING CALCULATOR")
    print("=" * 60)
    print()
    
    # Example: 3kW load for 8 hours
    sizing = generate_system_sizing_recommendation(
        load_watts=3000,
        daily_hours=8,
        sun_hours=5.5,
        battery_days_autonomy=1
    )
    
    print("Load Requirements: 3000W for 8 hours/day (24kWh)")
    print()
    print("Calculated Sizing:")
    print(f"  Panel Watts Needed: {sizing['panel_watts_needed']:.0f}W")
    print(f"  Battery Wh Needed: {sizing['battery_wh_needed']:.0f}Wh")
    print(f"  Inverter Watts Needed: {sizing['inverter_watts_needed']:.0f}W")
    print()
    print("Recommendations:")
    for rec in sizing.get("recommendations", []):
        print(f"  {rec['category'].upper()}: {rec['description']}")
        print(f"    Hint: {rec['hint']}")
        print()


if __name__ == "__main__":
    # Run basic simulation
    result = run_example_simulation()
    
    # Run oversized load scenario
    run_oversized_load_simulation()
    
    # Show sizing calculator
    run_sizing_calculator_example()
    
    print()
    print("Example simulation complete!")
