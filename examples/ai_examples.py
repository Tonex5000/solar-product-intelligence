"""
Example AI Explanation Queries.

This script demonstrates how to use the AI Explanation Layer
with various query types and explanation levels.
"""
import json
import sys
sys.path.insert(0, '/workspace/project/solar-product-intelligence')

from app.schemas.ai import (
    ExplanationLevel,
    ExplainSimulationRequest,
    DatasheetQueryRequest,
    DiagnoseRequest,
    RecommendRequest,
)
from app.services.prompt_templates import PromptTemplates
from app.services.context_builder import ContextBuilder


def example_prompt_context():
    """Show example prompt context building."""
    
    print("=" * 70)
    print("AI EXPLANATION LAYER - EXAMPLE PROMPTS")
    print("=" * 70)
    
    # Example simulation context
    example_context = {
        "simulation_input": {
            "simulation_days": 3650,
            "location": "california",
            "avg_sun_hours": 5.5,
            "load_watts": 2500,
            "daily_usage_hours": 10,
            "battery_id": 1,
            "inverter_id": 2,
            "panel_id": 3,
            "charge_controller_id": 4,
        },
        "simulation_summary": {
            "battery_health_final": 45.2,
            "total_energy_produced_kwh": 18250.0,
            "total_energy_consumed_kwh": 9125.0,
            "system_failures": 2,
            "warnings": 15,
            "cycle_count_total": 2500,
            "projected_battery_lifespan_years": 6.5,
        },
        "timeline_summary": {
            "simulation_days": 3650,
            "days_with_events": 45,
            "initial_battery_health": 100.0,
            "final_battery_health": 45.2,
        },
        "battery": {
            "product_name": "Tesla Powerwall 2",
            "model_name": "PG-001",
            "company": "Tesla",
            "specifications": {
                "voltage": {"value": "48", "unit": "V"},
                "capacity": {"value": "200", "unit": "Ah"},
                "max_discharge_current": {"value": "150", "unit": "A"},
                "cycle_life": {"value": "4000", "unit": "cycles"},
                "round_trip_efficiency": {"value": "90", "unit": "%"},
            },
        },
        "inverter": {
            "product_name": "SolarEdge SE5000H",
            "model_name": "SE5000H",
            "company": "SolarEdge",
            "specifications": {
                "rated_power": {"value": "5000", "unit": "W"},
                "surge_power": {"value": "7500", "unit": "W"},
                "efficiency": {"value": "99.2", "unit": "%"},
            },
        },
        "panel": {
            "product_name": "LG NeON 2",
            "model_name": "LG400N2W-A5",
            "company": "LG",
            "specifications": {
                "wattage": {"value": "400", "unit": "W"},
                "Voc": {"value": "48.9", "unit": "V"},
                "Isc": {"value": "10.3", "unit": "A"},
            },
        },
        "charge_controller": {
            "product_name": "Victron SmartSolar",
            "model_name": "MPPT 100/30",
            "company": "Victron Energy",
            "specifications": {
                "rated_current": {"value": "30", "unit": "A"},
                "max_input_voltage": {"value": "100", "unit": "V"},
                "efficiency": {"value": "98", "unit": "%"},
            },
        },
        "events": [
            {"day": 120, "type": "warning", "severity": "medium", "message": "Battery exceeded safe discharge current"},
            {"day": 365, "type": "damage", "severity": "high", "message": "Battery exceeded safe DoD (85% > 80%)"},
            {"day": 730, "type": "milestone", "severity": "low", "message": "Battery at year 2: Health=85%, Cycles=500"},
            {"day": 1000, "type": "failure", "severity": "critical", "message": "Inverter surge failure"},
        ],
    }
    
    print("\n### Example Query 1: Why did the battery degrade fast? ###")
    print("(Level: Intermediate)")
    
    # Create mock context object
    class MockContext:
        def __init__(self, data):
            self.simulation_input = data.get("simulation_input", {})
            self.simulation_summary = data.get("simulation_summary", {})
            self.timeline_summary = data.get("timeline_summary", {})
            self.battery = data.get("battery", {})
            self.inverter = data.get("inverter", {})
            self.panel = data.get("panel", {})
            self.charge_controller = data.get("charge_controller", {})
            self.events = data.get("events", [])
            self.datasheet_snippets = []
    
    context = MockContext(example_context)
    
    context_str = PromptTemplates.build_simulation_explanation_context(
        context=context,
        question="Why did the battery degrade so fast?",
        level=ExplanationLevel.INTERMEDIATE
    )
    
    print("\nContext sent to LLM:")
    print("-" * 50)
    print(context_str[:2000] + "..." if len(context_str) > 2000 else context_str)
    
    print("\n### Example Query 2: Explain like an engineer ###")
    print("(Level: Engineer)")
    
    context_str = PromptTemplates.build_simulation_explanation_context(
        context=context,
        question="What are the degradation mechanisms at play?",
        level=ExplanationLevel.ENGINEER
    )
    
    print("\nContext sent to LLM:")
    print("-" * 50)
    print(context_str[:2000] + "..." if len(context_str) > 2000 else context_str)
    
    print("\n### Example Query 3: Beginner explanation ###")
    print("(Level: Beginner)")
    
    context_str = PromptTemplates.build_simulation_explanation_context(
        context=context,
        question="What happened to my battery?",
        level=ExplanationLevel.BEGINNER
    )
    
    print("\nContext sent to LLM:")
    print("-" * 50)
    print(context_str[:1500] + "..." if len(context_str) > 1500 else context_str)


def example_system_prompts():
    """Show example system prompts for different levels."""
    
    print("\n" + "=" * 70)
    print("SYSTEM PROMPTS BY EXPLANATION LEVEL")
    print("=" * 70)
    
    for level in ExplanationLevel:
        prompt = PromptTemplates.get_system_prompt(level)
        print(f"\n### {level.value.upper()} ###")
        print("-" * 50)
        print(prompt[:800] + "..." if len(prompt) > 800 else prompt)


def example_diagnosis_context():
    """Show diagnosis context example."""
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS CONTEXT EXAMPLE")
    print("=" * 70)
    
    example_context = {
        "simulation_summary": {
            "battery_health_final": 45.2,
            "system_failures": 2,
            "warnings": 15,
            "max_inverter_load_percent": 95.0,
        },
        "battery": {
            "model_name": "Tesla Powerwall 2",
            "specifications": {
                "voltage": {"value": "48", "unit": "V"},
                "capacity": {"value": "200", "unit": "Ah"},
            },
        },
        "inverter": {
            "model_name": "SolarEdge SE5000H",
            "specifications": {
                "rated_power": {"value": "5000", "unit": "W"},
            },
        },
        "events": [
            {"day": 120, "type": "warning", "severity": "medium", "message": "Battery exceeded safe discharge current"},
            {"day": 365, "type": "damage", "severity": "high", "message": "Battery exceeded safe DoD"},
            {"day": 1000, "type": "failure", "severity": "critical", "message": "Inverter surge failure"},
        ],
    }
    
    class MockContext:
        def __init__(self, data):
            self.simulation_summary = data.get("simulation_summary", {})
            self.battery = data.get("battery", {})
            self.inverter = data.get("inverter", {})
            self.panel = data.get("panel", {})
            self.charge_controller = data.get("charge_controller", {})
            self.events = data.get("events", [])
    
    context = MockContext(example_context)
    
    diagnosis_str = PromptTemplates.build_diagnosis_context(context)
    
    print("\nDiagnosis context:")
    print("-" * 50)
    print(diagnosis_str)


def example_recommendation_context():
    """Show recommendation context example."""
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION CONTEXT EXAMPLE")
    print("=" * 70)
    
    example_context = {
        "simulation_input": {
            "load_watts": 2500,
            "daily_usage_hours": 10,
        },
        "simulation_summary": {
            "battery_health_final": 45.2,
            "system_failures": 2,
        },
        "battery": {
            "model_name": "Tesla Powerwall 2",
            "specifications": {
                "voltage": {"value": "48", "unit": "V"},
                "capacity": {"value": "200", "unit": "Ah"},
                "battery_type": {"value": "lithium", "unit": ""},
            },
        },
        "inverter": {
            "model_name": "SolarEdge SE5000H",
            "specifications": {
                "rated_power": {"value": "5000", "unit": "W"},
            },
        },
        "panel": {
            "model_name": "LG NeON 2",
            "specifications": {
                "wattage": {"value": "400", "unit": "W"},
            },
        },
        "charge_controller": {
            "model_name": "Victron SmartSolar",
            "specifications": {
                "rated_current": {"value": "30", "unit": "A"},
            },
        },
    }
    
    class MockContext:
        def __init__(self, data):
            self.simulation_input = data.get("simulation_input", {})
            self.simulation_summary = data.get("simulation_summary", {})
            self.battery = data.get("battery", {})
            self.inverter = data.get("inverter", {})
            self.panel = data.get("panel", {})
            self.charge_controller = data.get("charge_controller", {})
    
    context = MockContext(example_context)
    
    rec_str = PromptTemplates.build_recommendation_context(context, focus_area="battery")
    
    print("\nRecommendation context (focus: battery):")
    print("-" * 50)
    print(rec_str)


def show_api_examples():
    """Show example API request/response formats."""
    
    print("\n" + "=" * 70)
    print("API REQUEST/RESPONSE EXAMPLES")
    print("=" * 70)
    
    print("\n### 1. POST /ai/explain ###")
    print("Request:")
    explain_req = ExplainSimulationRequest(
        simulation_id=1,
        question="Why did my battery fail after 3 years?",
        level=ExplanationLevel.INTERMEDIATE
    )
    print(json.dumps(explain_req.model_dump(), indent=2))
    
    print("\nResponse:")
    print("""{
  "answer": "Your battery degraded rapidly due to operating at depths of discharge...",
  "key_factors": [
    "Excessive DoD (>80%) accelerated degradation",
    "High cycle count exceeded design parameters"
  ],
  "referenced_specs": [
    {"product_name": "Tesla Powerwall 2", "spec_key": "cycle_life", "spec_value": "4000"}
  ],
  "events_used": [
    {"day": 365, "type": "damage", "message": "Battery exceeded safe DoD"}
  ],
  "confidence": 0.85
}""")
    
    print("\n### 2. POST /ai/datasheet-query ###")
    print("Request:")
    datasheet_req = DatasheetQueryRequest(
        product_id=1,
        question="What is the maximum continuous discharge current?",
        level=ExplanationLevel.ENGINEER
    )
    print(json.dumps(datasheet_req.model_dump(), indent=2))
    
    print("\n### 3. POST /ai/diagnose ###")
    print("Request:")
    diagnose_req = DiagnoseRequest(
        simulation_id=1,
        level=ExplanationLevel.INTERMEDIATE
    )
    print(json.dumps(diagnose_req.model_dump(), indent=2))
    
    print("\n### 4. POST /ai/recommend ###")
    print("Request:")
    rec_req = RecommendRequest(
        simulation_id=1,
        focus_area="battery",
        level=ExplanationLevel.INTERMEDIATE
    )
    print(json.dumps(rec_req.model_dump(), indent=2))


def main():
    """Run all examples."""
    example_prompt_context()
    example_system_prompts()
    example_diagnosis_context()
    example_recommendation_context()
    show_api_examples()
    
    print("\n" + "=" * 70)
    print("NOTE: To use these endpoints, ensure GROQ_API_KEY is set")
    print("Example: export GROQ_API_KEY='your-api-key'")
    print("=" * 70)


if __name__ == "__main__":
    main()
