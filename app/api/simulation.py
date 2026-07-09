"""Simulation API routes."""
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.simulation import SimulationHistory, SimulationStatusEnum
from app.schemas import SimulationInput, SimulationOutput
from app.services.spec_loader import SpecLoader, SpecLoaderError
from app.services.simulation_engine import SolarSimulationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("/", response_model=SimulationOutput)
async def run_simulation(
    input_data: SimulationInput,
    save: bool = Query(False, description="Save simulation to history"),
    db: Session = Depends(get_db)
):
    """
    Run a solar system simulation.
    
    Simulates realistic solar installation behavior over time, including:
    - Battery degradation
    - Overload damage
    - Inverter stress/failure
    - Charge controller limits
    - System imbalance effects
    
    Returns detailed timeline, events, and recommendations.
    """
    try:
        # Load specs from database
        spec_loader = SpecLoader(db)
        
        # Validate system compatibility
        validation = spec_loader.validate_system(
            battery_id=input_data.battery_id,
            inverter_id=input_data.inverter_id,
            panel_id=input_data.panel_id,
            controller_id=input_data.charge_controller_id
        )
        
        if not validation.valid:
            errors = "\n".join([e.message for e in validation.errors])
            raise HTTPException(
                status_code=400,
                detail=f"System validation failed:\n{errors}"
            )
        
        # Load component specifications
        specs = spec_loader.load_all_specs(
            battery_id=input_data.battery_id,
            inverter_id=input_data.inverter_id,
            panel_id=input_data.panel_id,
            controller_id=input_data.charge_controller_id
        )
        
        # Create and run simulation
        engine = SolarSimulationEngine(specs=specs, input_params=input_data)
        result = engine.run()
        
        # Save to history if requested
        if save:
            history = SimulationHistory(
                status=SimulationStatusEnum.COMPLETED.value,
                battery_id=input_data.battery_id,
                inverter_id=input_data.inverter_id,
                panel_id=input_data.panel_id,
                charge_controller_id=input_data.charge_controller_id,
                load_watts=input_data.load_watts,
                daily_usage_hours=input_data.daily_usage_hours,
                simulation_days=input_data.simulation_days,
                location=input_data.location or "default",
                avg_sun_hours=input_data.avg_sun_hours or 5,
                summary_json=json.dumps(result.summary.model_dump()),
                full_results_json=json.dumps({
                    "timeline": [t.model_dump() for t in result.timeline],
                    "events": [e.model_dump() for e in result.events]
                }),
                recommendations_json=json.dumps([r.model_dump() for r in result.recommendations]),
                completed_at=result.completed_at,
                duration_ms=result.duration_ms
            )
            db.add(history)
            db.commit()
            db.refresh(history)
            result.id = history.id
        
        return result
        
    except SpecLoaderError as e:
        logger.error(f"Spec loader error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Simulation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/{simulation_id}", response_model=SimulationOutput)
async def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """Get a saved simulation by ID."""
    history = db.query(SimulationHistory).filter(
        SimulationHistory.id == simulation_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    try:
        # Reconstruct full result
        full_results = json.loads(history.full_results_json) if history.full_results_json else {}
        
        return SimulationOutput(
            id=history.id,
            status=history.status,
            input=SimulationInput(
                battery_id=history.battery_id,
                inverter_id=history.inverter_id,
                panel_id=history.panel_id,
                charge_controller_id=history.charge_controller_id,
                load_watts=history.load_watts,
                daily_usage_hours=history.daily_usage_hours,
                simulation_days=history.simulation_days,
                location=history.location,
                avg_sun_hours=history.avg_sun_hours
            ),
            specs=None,  # Not stored
            summary=json.loads(history.summary_json) if history.summary_json else None,
            timeline=full_results.get("timeline", []),
            events=full_results.get("events", []),
            recommendations=json.loads(history.recommendations_json) if history.recommendations_json else [],
            created_at=history.created_at,
            completed_at=history.completed_at,
            duration_ms=history.duration_ms
        )
    except Exception as e:
        logger.error(f"Error reconstructing simulation: {e}")
        raise HTTPException(status_code=500, detail="Failed to reconstruct simulation")


@router.get("/", response_model=dict)
async def list_simulations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """List all simulations with pagination."""
    total = db.query(SimulationHistory).count()
    pages = (total + page_size - 1) // page_size
    
    simulations = db.query(SimulationHistory).order_by(
        desc(SimulationHistory.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": [s.to_dict() for s in simulations],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.delete("/{simulation_id}")
async def delete_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a saved simulation."""
    history = db.query(SimulationHistory).filter(
        SimulationHistory.id == simulation_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    db.delete(history)
    db.commit()
    
    return {"message": "Simulation deleted successfully"}


@router.post("/validate")
async def validate_system(
    battery_id: int,
    inverter_id: int,
    panel_id: int,
    charge_controller_id: int,
    db: Session = Depends(get_db)
):
    """
    Validate system compatibility before running simulation.
    
    Checks that all components are verified, have required specs,
    and are electrically compatible.
    """
    try:
        spec_loader = SpecLoader(db)
        result = spec_loader.validate_system(
            battery_id=battery_id,
            inverter_id=inverter_id,
            panel_id=panel_id,
            controller_id=charge_controller_id
        )
        return result
    except SpecLoaderError as e:
        return {
            "valid": False,
            "errors": [{"field": "product_id", "message": str(e)}],
            "warnings": []
        }


@router.get("/sizing/calculate")
async def calculate_system_sizing(
    load_watts: float = Query(..., gt=0, description="Average load in watts"),
    daily_usage_hours: float = Query(..., gt=0, le=24, description="Daily usage hours"),
    location: str = Query("default", description="Location for sun hours"),
    battery_days_autonomy: int = Query(1, ge=1, le=7, description="Days of battery autonomy")
):
    """
    Calculate recommended system sizing based on load requirements.
    
    Provides recommendations for:
    - Panel wattage needed
    - Battery capacity needed
    - Inverter size needed
    """
    from app.services.recommendation_engine import generate_system_sizing_recommendation
    from app.services.simulation_engine import LOCATION_SUN_HOURS
    
    sun_hours = LOCATION_SUN_HOURS.get(location.lower(), 5.0)
    
    result = generate_system_sizing_recommendation(
        load_watts=load_watts,
        daily_hours=daily_usage_hours,
        sun_hours=sun_hours,
        battery_days_autonomy=battery_days_autonomy
    )
    
    # Add helpful context
    daily_kwh = result["daily_energy_kwh"]
    result["recommendations"] = [
        {
            "category": "panel",
            "description": f"Total panel wattage recommended: {result['panel_watts_needed']:.0f}W",
            "hint": "Round up to standard panel sizes (e.g., 400W panels)"
        },
        {
            "category": "battery",
            "description": f"Battery capacity recommended: {result['battery_wh_needed']:.0f}Wh",
            "hint": f"Consider {result['battery_wh_needed'] / 48:.0f}Ah at 48V for lithium batteries"
        },
        {
            "category": "inverter",
            "description": f"Inverter size recommended: {result['inverter_watts_needed']:.0f}W",
            "hint": "Choose pure sine wave inverter with at least 25% overhead"
        },
        {
            "category": "system_balance",
            "description": f"With {sun_hours:.1f} sun hours in {location}, you'll produce ~{daily_kwh:.2f}kWh daily",
            "hint": "Ensure your panel orientation and tilt are optimized"
        }
    ]
    
    return result
