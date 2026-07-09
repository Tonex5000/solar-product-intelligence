"""Prompt Templates for AI Explanation Layer."""
import json
from typing import Optional

from app.schemas.ai import (
    ExplanationLevel,
    SYSTEM_PROMPTS,
    AIContext,
)


class PromptTemplates:
    """
    Prompt Templates for AI Explanations.
    
    Provides structured prompts for different explanation types.
    """
    
    @staticmethod
    def get_system_prompt(level: ExplanationLevel) -> str:
        """Get system prompt for the explanation level."""
        template = SYSTEM_PROMPTS.get(level, SYSTEM_PROMPTS[ExplanationLevel.INTERMEDIATE])
        return f"""{template.role}

CRITICAL RULES:
{chr(10).join(f"- {rule}" for rule in template.rules)}

OUTPUT FORMAT:
{template.output_format}

ANTI-HALLUCINATION RULE: If you cannot find the answer in the provided context data, you MUST say "This information is not available in the provided data." Never make up specifications or values."""

    @staticmethod
    def build_simulation_explanation_context(
        context: AIContext,
        question: str,
        level: ExplanationLevel
    ) -> str:
        """Build context string for simulation explanation."""
        parts = []
        
        # Simulation Configuration
        parts.append("=== SIMULATION CONFIGURATION ===")
        sim_input = context.simulation_input
        if sim_input:
            parts.append(f"Simulation Duration: {sim_input.get('simulation_days', 'N/A')} days")
            parts.append(f"Location: {sim_input.get('location', 'N/A')}")
            parts.append(f"Average Sun Hours: {sim_input.get('avg_sun_hours', 'N/A')}")
            parts.append(f"Load: {sim_input.get('load_watts', 'N/A')}W for {sim_input.get('daily_usage_hours', 'N/A')} hours/day")
        
        # Simulation Summary
        parts.append("\n=== SIMULATION RESULTS SUMMARY ===")
        summary = context.simulation_summary
        if summary:
            parts.append(f"Final Battery Health: {summary.get('battery_health_final', 'N/A')}%")
            parts.append(f"Total Cycles: {summary.get('cycle_count_total', 'N/A')}")
            parts.append(f"System Failures: {summary.get('system_failures', 'N/A')}")
            parts.append(f"Warnings: {summary.get('warnings', 'N/A')}")
            parts.append(f"Total Energy Produced: {summary.get('total_energy_produced_kwh', 'N/A')} kWh")
            parts.append(f"Total Energy Consumed: {summary.get('total_energy_consumed_kwh', 'N/A')} kWh")
            parts.append(f"Projected Battery Lifespan: {summary.get('projected_battery_lifespan_years', 'N/A')} years")
        
        # Timeline Summary
        parts.append("\n=== TIMELINE SUMMARY ===")
        tl_summary = context.timeline_summary
        if tl_summary:
            parts.append(f"Days Simulated: {tl_summary.get('simulation_days', 'N/A')}")
            parts.append(f"Days with Events: {tl_summary.get('days_with_events', 'N/A')}")
            parts.append(f"Initial Battery Health: {tl_summary.get('initial_battery_health', 'N/A')}%")
            parts.append(f"Final Battery Health: {tl_summary.get('final_battery_health', 'N/A')}%")
        
        # Battery Specs
        battery = context.battery
        if battery:
            parts.append("\n=== BATTERY SPECIFICATIONS ===")
            parts.append(f"Product: {battery.get('product_name', 'N/A')}")
            parts.append(f"Model: {battery.get('model_name', 'N/A')}")
            parts.append(f"Manufacturer: {battery.get('company', 'N/A')}")
            specs = battery.get('specifications', {})
            for key, value in specs.items():
                if isinstance(value, dict):
                    unit = value.get('unit', '')
                    val = value.get('value', 'N/A')
                    parts.append(f"  {key}: {val} {unit}")
                else:
                    parts.append(f"  {key}: {value}")
            if battery.get('datasheet_snippet'):
                parts.append(f"\nDatasheet excerpt:\n{battery['datasheet_snippet'][:500]}")
        
        # Inverter Specs
        inverter = context.inverter
        if inverter:
            parts.append("\n=== INVERTER SPECIFICATIONS ===")
            parts.append(f"Product: {inverter.get('product_name', 'N/A')}")
            parts.append(f"Model: {inverter.get('model_name', 'N/A')}")
            parts.append(f"Manufacturer: {inverter.get('company', 'N/A')}")
            specs = inverter.get('specifications', {})
            for key, value in specs.items():
                if isinstance(value, dict):
                    unit = value.get('unit', '')
                    val = value.get('value', 'N/A')
                    parts.append(f"  {key}: {val} {unit}")
                else:
                    parts.append(f"  {key}: {value}")
        
        # Panel Specs
        panel = context.panel
        if panel:
            parts.append("\n=== SOLAR PANEL SPECIFICATIONS ===")
            parts.append(f"Product: {panel.get('product_name', 'N/A')}")
            parts.append(f"Model: {panel.get('model_name', 'N/A')}")
            parts.append(f"Manufacturer: {panel.get('company', 'N/A')}")
            specs = panel.get('specifications', {})
            for key, value in specs.items():
                if isinstance(value, dict):
                    unit = value.get('unit', '')
                    val = value.get('value', 'N/A')
                    parts.append(f"  {key}: {val} {unit}")
                else:
                    parts.append(f"  {key}: {value}")
        
        # Charge Controller Specs
        controller = context.charge_controller
        if controller:
            parts.append("\n=== CHARGE CONTROLLER SPECIFICATIONS ===")
            parts.append(f"Product: {controller.get('product_name', 'N/A')}")
            parts.append(f"Model: {controller.get('model_name', 'N/A')}")
            parts.append(f"Manufacturer: {controller.get('company', 'N/A')}")
            specs = controller.get('specifications', {})
            for key, value in specs.items():
                if isinstance(value, dict):
                    unit = value.get('unit', '')
                    val = value.get('value', 'N/A')
                    parts.append(f"  {key}: {val} {unit}")
                else:
                    parts.append(f"  {key}: {value}")
        
        # Key Events
        if context.events:
            parts.append("\n=== KEY SIMULATION EVENTS ===")
            # Show first 20 events
            events_to_show = context.events[:20]
            for event in events_to_show:
                day = event.get('day', '?')
                event_type = event.get('type', 'unknown')
                severity = event.get('severity', 'low')
                message = event.get('message', '')
                parts.append(f"[Day {day}] [{event_type.upper()}] {message}")
            
            if len(context.events) > 20:
                parts.append(f"... and {len(context.events) - 20} more events")
        
        return "\n".join(parts)
    
    @staticmethod
    def build_datasheet_query_context(
        product_context: dict,
        question: str
    ) -> str:
        """Build context for datasheet query."""
        parts = []
        
        parts.append("=== PRODUCT INFORMATION ===")
        parts.append(f"Product: {product_context.get('product_name', 'N/A')}")
        parts.append(f"Model: {product_context.get('model_name', 'N/A')}")
        parts.append(f"Manufacturer: {product_context.get('company', 'N/A')}")
        parts.append(f"Category: {product_context.get('category', 'N/A')}")
        parts.append(f"Verified: {product_context.get('is_verified', False)}")
        
        parts.append("\n=== SPECIFICATIONS ===")
        specs = product_context.get('specifications', {})
        for key, value in specs.items():
            if isinstance(value, dict):
                unit = value.get('unit', '')
                val = value.get('value', 'N/A')
                parts.append(f"  {key}: {val} {unit}")
            else:
                parts.append(f"  {key}: {value}")
        
        parts.append("\n=== DOCUMENT CONTENT ===")
        documents = product_context.get('documents', [])
        for doc in documents:
            doc_type = doc.get('type', 'unknown')
            text = doc.get('text', '')
            parts.append(f"\n--- {doc_type.upper()} ---")
            parts.append(text)
        
        return "\n".join(parts)
    
    @staticmethod
    def build_diagnosis_context(context: AIContext) -> str:
        """Build context for system diagnosis."""
        parts = []
        
        # Overall System Health
        parts.append("=== SYSTEM HEALTH ASSESSMENT ===")
        summary = context.simulation_summary
        if summary:
            health = summary.get('battery_health_final', 0)
            failures = summary.get('system_failures', 0)
            warnings = summary.get('warnings', 0)
            
            if health > 80:
                health_status = "GOOD"
            elif health > 50:
                health_status = "FAIR"
            elif health > 20:
                health_status = "POOR"
            else:
                health_status = "CRITICAL"
            
            parts.append(f"Overall Health Score: {health}% ({health_status})")
            parts.append(f"System Failures: {failures}")
            parts.append(f"Warnings: {warnings}")
        
        # Component Analysis
        parts.append("\n=== COMPONENT ANALYSIS ===")
        
        # Battery Analysis
        battery = context.battery
        if battery:
            parts.append("\n--- BATTERY ---")
            parts.append(f"Model: {battery.get('model_name', 'N/A')}")
            specs = battery.get('specifications', {})
            parts.append(f"Voltage: {specs.get('voltage', {}).get('value', 'N/A')} {specs.get('voltage', {}).get('unit', 'V')}")
            parts.append(f"Capacity: {specs.get('capacity', {}).get('value', 'N/A')} {specs.get('capacity', {}).get('unit', 'Ah')}")
            
            if summary:
                final_health = summary.get('battery_health_final', 100)
                if final_health < 50:
                    parts.append("⚠️ Battery health below 50% - replacement may be needed")
        
        # Inverter Analysis
        inverter = context.inverter
        if inverter:
            parts.append("\n--- INVERTER ---")
            parts.append(f"Model: {inverter.get('model_name', 'N/A')}")
            specs = inverter.get('specifications', {})
            parts.append(f"Rated Power: {specs.get('rated_power', {}).get('value', 'N/A')} {specs.get('rated_power', {}).get('unit', 'W')}")
            
            if summary:
                max_load = summary.get('max_inverter_load_percent', 0)
                if max_load > 100:
                    parts.append(f"⚠️ Inverter overloaded to {max_load}% - risk of failure")
                elif max_load > 85:
                    parts.append(f"⚠️ Inverter running near capacity ({max_load}%)")
        
        # Events Analysis
        parts.append("\n=== EVENT ANALYSIS ===")
        if context.events:
            # Count events by type
            event_counts = {}
            for event in context.events:
                event_type = event.get('type', 'unknown')
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            parts.append(f"Total Events: {len(context.events)}")
            for event_type, count in event_counts.items():
                parts.append(f"  {event_type}: {count}")
            
            # Show critical events
            critical = [e for e in context.events if e.get('severity') in ['critical', 'high']]
            if critical:
                parts.append(f"\nCritical/High Severity Events ({len(critical)}):")
                for event in critical[:10]:
                    parts.append(f"  [Day {event.get('day')}] {event.get('message')}")
        
        return "\n".join(parts)
    
    @staticmethod
    def build_recommendation_context(
        context: AIContext,
        focus_area: Optional[str] = None
    ) -> str:
        """Build context for recommendations."""
        parts = []
        
        parts.append("=== CURRENT SYSTEM CONFIGURATION ===")
        
        if context.battery:
            parts.append("\n--- BATTERY ---")
            battery = context.battery
            parts.append(f"Model: {battery.get('model_name', 'N/A')}")
            specs = battery.get('specifications', {})
            parts.append(f"Voltage: {specs.get('voltage', {}).get('value', 'N/A')}V")
            parts.append(f"Capacity: {specs.get('capacity', {}).get('value', 'N/A')} Ah")
            parts.append(f"Type: {specs.get('battery_type', {}).get('value', 'Unknown')}")
        
        if context.inverter:
            parts.append("\n--- INVERTER ---")
            inverter = context.inverter
            parts.append(f"Model: {inverter.get('model_name', 'N/A')}")
            specs = inverter.get('specifications', {})
            parts.append(f"Rated Power: {specs.get('rated_power', {}).get('value', 'N/A')} W")
        
        if context.panel:
            parts.append("\n--- SOLAR PANELS ---")
            panel = context.panel
            parts.append(f"Model: {panel.get('model_name', 'N/A')}")
            specs = panel.get('specifications', {})
            parts.append(f"Wattage: {specs.get('wattage', {}).get('value', 'N/A')} W")
        
        if context.charge_controller:
            parts.append("\n--- CHARGE CONTROLLER ---")
            controller = context.charge_controller
            parts.append(f"Model: {controller.get('model_name', 'N/A')}")
            specs = controller.get('specifications', {})
            parts.append(f"Rated Current: {specs.get('rated_current', {}).get('value', 'N/A')} A")
        
        parts.append("\n=== LOAD REQUIREMENTS ===")
        sim_input = context.simulation_input
        if sim_input:
            parts.append(f"Power: {sim_input.get('load_watts', 'N/A')} W")
            parts.append(f"Daily Usage: {sim_input.get('daily_usage_hours', 'N/A')} hours")
            daily_wh = sim_input.get('load_watts', 0) * sim_input.get('daily_usage_hours', 0)
            parts.append(f"Daily Energy: {daily_wh} Wh ({daily_wh/1000:.2f} kWh)")
        
        parts.append("\n=== PROBLEMS DETECTED ===")
        summary = context.simulation_summary
        if summary:
            if summary.get('system_failures', 0) > 0:
                parts.append(f"⚠️ {summary['system_failures']} system failures detected")
            if summary.get('warnings', 0) > 5:
                parts.append(f"⚠️ {summary['warnings']} warnings generated")
            
            health = summary.get('battery_health_final', 100)
            if health < 50:
                parts.append(f"⚠️ Battery health critical ({health}%)")
        
        if focus_area:
            parts.append(f"\n=== FOCUS AREA: {focus_area.upper()} ===")
        
        return "\n".join(parts)
