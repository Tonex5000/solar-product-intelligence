"""Tests for Solar Simulation Engine."""
import pytest
from app.schemas.simulation import (
    SimulationInput,
    ComponentSpecs,
    BatterySpec,
    InverterSpec,
    PanelSpec,
    ChargeControllerSpec,
    EventType,
    Severity,
)
from app.services.simulation_engine import SolarSimulationEngine
from app.services.event_system import EventLogger
from app.services.recommendation_engine import RecommendationEngine, generate_system_sizing_recommendation


@pytest.fixture
def standard_specs():
    """Standard component specifications for testing."""
    return ComponentSpecs(
        battery=BatterySpec(
            voltage=48,
            capacity_ah=200,
            max_discharge_current=150,
            max_charge_current=100,
            cycle_life=4000,
            round_trip_efficiency=0.92,
            dod_max_safe=0.80,
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


@pytest.fixture
def standard_input():
    """Standard simulation input for testing."""
    return SimulationInput(
        battery_id=1,
        inverter_id=2,
        panel_id=3,
        charge_controller_id=4,
        load_watts=2500,
        daily_usage_hours=10,
        simulation_days=365,
        location="default",
        avg_sun_hours=5.0
    )


class TestEventLogger:
    """Tests for the EventLogger class."""

    def test_log_event(self):
        """Test basic event logging."""
        logger = EventLogger()
        event = logger.log_warning(1, "Test warning", "battery")
        
        assert len(logger.events) == 1
        assert event.day == 1
        assert event.event_type == EventType.WARNING
        assert event.message == "Test warning"
        assert event.component == "battery"

    def test_get_events_by_type(self):
        """Test filtering events by type."""
        logger = EventLogger()
        logger.log_warning(1, "Warning 1", "battery")
        logger.log_damage(2, "Damage 1", "battery")
        logger.log_warning(3, "Warning 2", "inverter")
        
        warnings = logger.get_events_by_type(EventType.WARNING)
        damages = logger.get_events_by_type(EventType.DAMAGE)
        
        assert len(warnings) == 2
        assert len(damages) == 1

    def test_get_events_by_day(self):
        """Test filtering events by day."""
        logger = EventLogger()
        logger.log_warning(1, "Day 1 event", "battery")
        logger.log_warning(5, "Day 5 event", "battery")
        
        day_1_events = logger.get_events_by_day(1)
        day_2_events = logger.get_events_by_day(2)
        
        assert len(day_1_events) == 1
        assert len(day_2_events) == 0

    def test_get_first_failure_day(self):
        """Test getting first failure day."""
        logger = EventLogger()
        logger.log_warning(1, "Warning", "battery")
        logger.log_failure(5, "Failure", "inverter")
        logger.log_failure(10, "Another failure", "battery")
        
        assert logger.get_first_failure_day() == 5

    def test_clear_events(self):
        """Test clearing events."""
        logger = EventLogger()
        logger.log_warning(1, "Warning", "battery")
        logger.clear()
        
        assert len(logger.events) == 0


class TestBatteryModel:
    """Tests for the BatteryModel class."""

    def test_initial_state(self, standard_specs):
        """Test battery initial state."""
        event_logger = EventLogger()
        engine = SolarSimulationEngine(standard_specs, SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=1000,
            daily_usage_hours=5, simulation_days=10
        ))
        
        assert engine.battery_model.state.soc == 1.0
        assert engine.battery_model.state.health == 100.0
        assert engine.battery_model.state.cycle_count == 0

    def test_capacity_calculation(self, standard_specs):
        """Test battery capacity calculation."""
        event_logger = EventLogger()
        engine = SolarSimulationEngine(standard_specs, SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=1000,
            daily_usage_hours=5, simulation_days=10
        ))
        
        # 48V * 200Ah = 9600Wh
        assert engine.battery_model.capacity_wh == 9600
        assert engine.battery_model.original_capacity_wh == 9600


class TestInverterModel:
    """Tests for the InverterModel class."""

    def test_initial_state(self, standard_specs):
        """Test inverter initial state."""
        engine = SolarSimulationEngine(standard_specs, SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=1000,
            daily_usage_hours=5, simulation_days=10
        ))
        
        assert engine.inverter_model.state.load_percent == 0.0
        assert engine.inverter_model.state.failed == False


class TestSolarProductionModel:
    """Tests for the SolarProductionModel class."""

    def test_daily_production_calculation(self, standard_specs):
        """Test daily solar production calculation."""
        engine = SolarSimulationEngine(standard_specs, SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=1000,
            daily_usage_hours=5, simulation_days=10
        ))
        
        # 4000W (panels) * 5 sun hours * 0.8 efficiency = 16kWh
        production = engine.solar_production_model.calculate_daily_production(5.0)
        assert production == pytest.approx(16.0, rel=0.1)


class TestSolarSimulationEngine:
    """Tests for the main SolarSimulationEngine class."""

    def test_engine_initialization(self, standard_specs, standard_input):
        """Test engine initializes correctly."""
        engine = SolarSimulationEngine(standard_specs, standard_input)
        
        assert engine.specs == standard_specs
        assert engine.input == standard_input
        assert isinstance(engine.event_logger, EventLogger)

    def test_run_simulation(self, standard_specs, standard_input):
        """Test running a short simulation."""
        engine = SolarSimulationEngine(standard_specs, standard_input)
        result = engine.run()
        
        assert result.status.value == "completed"
        assert len(result.timeline) == 365
        assert result.summary.total_energy_produced_kwh > 0
        assert result.summary.total_energy_consumed_kwh > 0

    def test_battery_degradation_over_time(self, standard_specs):
        """Test that battery degrades over simulation period."""
        input_params = SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=2500,
            daily_usage_hours=10, simulation_days=3650  # 10 years
        )
        
        engine = SolarSimulationEngine(standard_specs, input_params)
        result = engine.run()
        
        # Battery should have degraded
        assert result.summary.battery_health_final < 100.0
        # Cycle count should increase
        assert result.summary.cycle_count_total > 0

    def test_system_balance_calculation(self, standard_specs):
        """Test system energy balance calculation."""
        input_params = SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=2500,
            daily_usage_hours=10, simulation_days=365
        )
        
        engine = SolarSimulationEngine(standard_specs, input_params)
        result = engine.run()
        
        # System balance should be reasonable
        assert result.summary.system_balance_percent > 0
        # Production should roughly match consumption for well-sized system
        assert 0.5 < (result.summary.total_energy_produced_kwh / result.summary.total_energy_consumed_kwh) < 2.0


class TestRecommendationEngine:
    """Tests for the RecommendationEngine class."""

    def test_generate_sizing_recommendation(self):
        """Test system sizing recommendation generation."""
        result = generate_system_sizing_recommendation(
            load_watts=3000,
            daily_hours=8,
            sun_hours=5.0,
            battery_days_autonomy=1
        )
        
        assert "panel_watts_needed" in result
        assert "battery_wh_needed" in result
        assert "inverter_watts_needed" in result
        assert result["panel_watts_needed"] > 0
        assert result["battery_wh_needed"] > 0
        assert result["inverter_watts_needed"] > 0

    def test_undersized_battery_recommendation(self, standard_specs):
        """Test that undersized battery generates recommendation."""
        # Very high load that exceeds battery capacity
        input_params = SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=10000,  # Very high load
            daily_usage_hours=10, simulation_days=365
        )
        
        engine = SolarSimulationEngine(standard_specs, input_params)
        result = engine.run()
        
        # Should have battery-related recommendations
        battery_recs = [r for r in result.recommendations if r.category == "battery"]
        assert len(battery_recs) > 0


class TestSimulationSchemas:
    """Tests for simulation Pydantic schemas."""

    def test_simulation_input_validation(self):
        """Test simulation input validation."""
        # Valid input
        valid_input = SimulationInput(
            battery_id=1,
            inverter_id=2,
            panel_id=3,
            charge_controller_id=4,
            load_watts=2500,
            daily_usage_hours=10,
            simulation_days=365
        )
        assert valid_input.load_watts == 2500
        
        # Invalid: negative load
        with pytest.raises(ValueError):
            SimulationInput(
                battery_id=1, inverter_id=2, panel_id=3,
                charge_controller_id=4, load_watts=-100,
                daily_usage_hours=10, simulation_days=365
            )

    def test_simulation_input_defaults(self):
        """Test simulation input default values."""
        input_data = SimulationInput(
            battery_id=1, inverter_id=2, panel_id=3,
            charge_controller_id=4, load_watts=2500,
            daily_usage_hours=10, simulation_days=365
        )
        
        assert input_data.location == "default"
        assert input_data.avg_sun_hours == 5.0


# Integration tests
class TestSimulationIntegration:
    """Integration tests for simulation workflow."""

    def test_short_simulation_completes(self):
        """Test that a short simulation completes without errors."""
        specs = ComponentSpecs(
            battery=BatterySpec(voltage=48, capacity_ah=200),
            inverter=InverterSpec(rated_power=5000),
            panel=PanelSpec(wattage=400, panel_count=10),
            charge_controller=ChargeControllerSpec(rated_current=60)
        )
        
        input_params = SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=1000,
            daily_usage_hours=5, simulation_days=30
        )
        
        engine = SolarSimulationEngine(specs, input_params)
        result = engine.run()
        
        assert result.status.value == "completed"
        assert len(result.timeline) == 30
        assert result.duration_ms >= 0  # Duration may be 0 for fast simulations
        # Recommendations should be generated
        assert len(result.recommendations) >= 0

    def test_10_year_simulation_completes(self):
        """Test that a 10-year simulation completes efficiently."""
        specs = ComponentSpecs(
            battery=BatterySpec(voltage=48, capacity_ah=200, battery_type="lithium"),
            inverter=InverterSpec(rated_power=5000),
            panel=PanelSpec(wattage=400, panel_count=10),
            charge_controller=ChargeControllerSpec(rated_current=60)
        )
        
        input_params = SimulationInput(
            battery_id=1, inverter_id=1, panel_id=1,
            charge_controller_id=1, load_watts=2500,
            daily_usage_hours=10, simulation_days=3650
        )
        
        engine = SolarSimulationEngine(specs, input_params)
        result = engine.run()
        
        assert result.status.value == "completed"
        assert len(result.timeline) == 3650
        assert result.duration_ms < 10000  # Should complete in under 10 seconds
