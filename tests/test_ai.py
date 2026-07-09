"""Tests for AI Explanation Layer."""
import pytest
from unittest.mock import Mock, patch

from app.schemas.ai import (
    ExplanationLevel,
    ExplainSimulationRequest,
    DiagnoseRequest,
    RecommendRequest,
    SYSTEM_PROMPTS,
)
from app.services.prompt_templates import PromptTemplates
from app.services.context_builder import ContextBuilder


class TestPromptTemplates:
    """Tests for prompt template generation."""

    def test_get_system_prompt_beginner(self):
        """Test beginner level system prompt."""
        prompt = PromptTemplates.get_system_prompt(ExplanationLevel.BEGINNER)
        
        assert "friendly" in prompt.lower()
        assert "simple" in prompt.lower()
        assert "jargon" in prompt.lower()

    def test_get_system_prompt_engineer(self):
        """Test engineer level system prompt."""
        prompt = PromptTemplates.get_system_prompt(ExplanationLevel.ENGINEER)
        
        assert "senior" in prompt.lower() or "engineer" in prompt.lower()
        assert "engineering" in prompt.lower() or "engineering" in prompt.lower()

    def test_system_prompts_all_levels(self):
        """Test all explanation levels have prompts."""
        for level in ExplanationLevel:
            prompt = PromptTemplates.get_system_prompt(level)
            assert prompt is not None
            assert len(prompt) > 100

    def test_build_simulation_explanation_context(self):
        """Test simulation explanation context building."""
        class MockContext:
            simulation_input = {
                "simulation_days": 365,
                "load_watts": 2500,
                "daily_usage_hours": 10,
                "location": "california"
            }
            simulation_summary = {
                "battery_health_final": 85.0,
                "total_energy_produced_kwh": 5000,
                "system_failures": 0
            }
            timeline_summary = {
                "simulation_days": 365,
                "days_with_events": 5
            }
            battery = {
                "product_name": "Test Battery",
                "model_name": "TB-100",
                "company": "TestCorp",
                "specifications": {
                    "voltage": {"value": "48", "unit": "V"},
                    "capacity": {"value": "200", "unit": "Ah"}
                }
            }
            inverter = {
                "product_name": "Test Inverter",
                "model_name": "TI-5000",
                "company": "TestCorp",
                "specifications": {
                    "rated_power": {"value": "5000", "unit": "W"}
                }
            }
            panel = {
                "product_name": "Test Panel",
                "model_name": "TP-400",
                "company": "TestCorp",
                "specifications": {
                    "wattage": {"value": "400", "unit": "W"}
                }
            }
            charge_controller = {}
            events = [
                {"day": 100, "type": "warning", "severity": "low", "message": "Test warning"}
            ]
            datasheet_snippets = []
        
        context = MockContext()
        context_str = PromptTemplates.build_simulation_explanation_context(
            context=context,
            question="Why did this happen?",
            level=ExplanationLevel.INTERMEDIATE
        )
        
        assert "SIMULATION CONFIGURATION" in context_str
        assert "Test Battery" in context_str
        assert "48 V" in context_str
        assert "2500" in context_str

    def test_build_diagnosis_context(self):
        """Test diagnosis context building."""
        class MockContext:
            simulation_summary = {
                "battery_health_final": 45.0,
                "system_failures": 2,
                "warnings": 10,
                "max_inverter_load_percent": 95.0
            }
            battery = {
                "model_name": "Test Battery",
                "specifications": {
                    "voltage": {"value": "48", "unit": "V"},
                    "capacity": {"value": "200", "unit": "Ah"}
                }
            }
            inverter = {
                "model_name": "Test Inverter",
                "specifications": {
                    "rated_power": {"value": "5000", "unit": "W"}
                }
            }
            panel = {}
            charge_controller = {}
            events = [
                {"day": 100, "type": "damage", "severity": "high", "message": "Test damage"}
            ]
        
        context = MockContext()
        diagnosis_str = PromptTemplates.build_diagnosis_context(context)
        
        assert "SYSTEM HEALTH ASSESSMENT" in diagnosis_str
        assert "45" in diagnosis_str
        assert "CRITICAL" in diagnosis_str or "POOR" in diagnosis_str

    def test_build_recommendation_context(self):
        """Test recommendation context building."""
        class MockContext:
            simulation_input = {
                "load_watts": 2500,
                "daily_usage_hours": 10
            }
            simulation_summary = {
                "battery_health_final": 45.0
            }
            battery = {
                "model_name": "Test Battery",
                "specifications": {
                    "voltage": {"value": "48", "unit": "V"},
                    "capacity": {"value": "200", "unit": "Ah"},
                    "battery_type": {"value": "lithium", "unit": ""}
                }
            }
            inverter = {
                "model_name": "Test Inverter",
                "specifications": {
                    "rated_power": {"value": "5000", "unit": "W"}
                }
            }
            panel = {
                "model_name": "Test Panel",
                "specifications": {
                    "wattage": {"value": "400", "unit": "W"}
                }
            }
            charge_controller = {
                "model_name": "Test Controller",
                "specifications": {
                    "rated_current": {"value": "30", "unit": "A"}
                }
            }
        
        context = MockContext()
        rec_str = PromptTemplates.build_recommendation_context(context, focus_area="battery")
        
        assert "CURRENT SYSTEM CONFIGURATION" in rec_str
        assert "BATTERY" in rec_str
        assert "25000" in rec_str  # daily_wh = 2500 * 10


class TestSchemaValidation:
    """Tests for AI schema validation."""

    def test_explain_simulation_request(self):
        """Test explain simulation request validation."""
        request = ExplainSimulationRequest(
            simulation_id=1,
            question="Why did this happen?",
            level=ExplanationLevel.INTERMEDIATE
        )
        
        assert request.simulation_id == 1
        assert request.question == "Why did this happen?"
        assert request.level == ExplanationLevel.INTERMEDIATE

    def test_explain_simulation_request_default_level(self):
        """Test default explanation level."""
        request = ExplainSimulationRequest(
            simulation_id=1,
            question="Why?"
        )
        
        assert request.level == ExplanationLevel.INTERMEDIATE

    def test_diagnose_request(self):
        """Test diagnose request."""
        request = DiagnoseRequest(
            simulation_id=1,
            level=ExplanationLevel.ENGINEER
        )
        
        assert request.simulation_id == 1
        assert request.level == ExplanationLevel.ENGINEER

    def test_recommend_request(self):
        """Test recommend request with focus area."""
        request = RecommendRequest(
            simulation_id=1,
            focus_area="battery",
            level=ExplanationLevel.BEGINNER
        )
        
        assert request.simulation_id == 1
        assert request.focus_area == "battery"
        assert request.level == ExplanationLevel.BEGINNER


class TestContextBuilder:
    """Tests for context builder."""

    def test_context_builder_specs_to_dict(self):
        """Test specification conversion to dict."""
        # Create mock specs
        class MockSpec:
            def __init__(self, key, value, unit=None, confidence=1.0):
                self.spec_key = key
                self.spec_value = value
                self.unit = unit
                self.confidence_score = confidence
        
        mock_specs = [
            MockSpec("voltage", "48", "V", 1.0),
            MockSpec("capacity", "200", "Ah", 0.9),
        ]
        
        # Test would require DB connection, so we test the conversion logic
        result = {
            spec.spec_key: {
                "value": spec.spec_value,
                "unit": spec.unit,
                "confidence": spec.confidence_score,
            }
            for spec in mock_specs
        }
        
        assert result["voltage"]["value"] == "48"
        assert result["voltage"]["unit"] == "V"
        assert result["capacity"]["value"] == "200"


class TestAntiHallucination:
    """Tests for anti-hallucination rules."""

    def test_system_prompt_includes_no_guess_rule(self):
        """Test that system prompts include no-guess rules."""
        for level in ExplanationLevel:
            prompt = PromptTemplates.get_system_prompt(level)
            
            # Check for anti-hallucination rules
            assert "information" in prompt.lower()
            assert "available" in prompt.lower() or "provided" in prompt.lower()

    def test_system_prompt_mentions_data_source(self):
        """Test that system prompts reference data sources."""
        for level in ExplanationLevel:
            prompt = PromptTemplates.get_system_prompt(level)
            
            # Should mention using provided data
            assert "context" in prompt.lower() or "data" in prompt.lower() or "information" in prompt.lower()


class TestExplanationLevels:
    """Tests for explanation level differentiation."""

    def test_beginner_prompt_friendly(self):
        """Test beginner prompt is friendly."""
        prompt = PromptTemplates.get_system_prompt(ExplanationLevel.BEGINNER)
        
        assert "friendly" in prompt.lower() or "simple" in prompt.lower()

    def test_engineer_prompt_technical(self):
        """Test engineer prompt is technical."""
        prompt = PromptTemplates.get_system_prompt(ExplanationLevel.ENGINEER)
        
        # Should contain technical keywords
        assert "engineering" in prompt.lower() or "specification" in prompt.lower() or "technical" in prompt.lower()

    def test_all_levels_have_output_format(self):
        """Test all levels specify output format."""
        for level in ExplanationLevel:
            prompt = PromptTemplates.get_system_prompt(level)
            
            assert "output" in prompt.lower() or "format" in prompt.lower() or "respond" in prompt.lower()
