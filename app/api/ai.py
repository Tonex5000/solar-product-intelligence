"""AI Explanation Layer API routes."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ai import (
    ExplanationLevel,
    ExplainSimulationRequest,
    ExplainSimulationResponse,
    DatasheetQueryRequest,
    DatasheetQueryResponse,
    DiagnoseRequest,
    DiagnoseResponse,
    RecommendRequest,
    RecommendResponse,
)
from app.services.ai_service import AIExplanationService, AIServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Explanations"])


def get_ai_service(db: Session = Depends(get_db)) -> AIExplanationService:
    """Dependency to get AI service instance."""
    return AIExplanationService(db=db)


@router.post("/explain", response_model=ExplainSimulationResponse)
async def explain_simulation(
    request: ExplainSimulationRequest,
    ai_service: AIExplanationService = Depends(get_ai_service)
):
    """
    Explain simulation outcomes.
    
    Ask questions about why certain events occurred, what caused battery degradation,
    or any other aspect of the simulation results.
    
    The AI will analyze the simulation data and provide explanations grounded
    in the actual specs and events.
    """
    try:
        result = ai_service.explain_simulation(
            simulation_id=request.simulation_id,
            question=request.question,
            level=request.level
        )
        return result
    except AIServiceError as e:
        logger.error(f"Explain simulation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in explain_simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate explanation")


@router.post("/datasheet-query", response_model=DatasheetQueryResponse)
async def query_datasheet(
    request: DatasheetQueryRequest,
    ai_service: AIExplanationService = Depends(get_ai_service)
):
    """
    Query a product's datasheet.
    
    Ask questions about specific product specifications, capabilities, or features.
    The AI will search the extracted datasheet text and provide answers with
    references to the source material.
    
    If the information is not available in the datasheet, the AI will clearly
    state this rather than making up an answer.
    """
    try:
        result = ai_service.query_datasheet(
            product_id=request.product_id,
            question=request.question,
            level=request.level
        )
        return result
    except AIServiceError as e:
        logger.error(f"Datasheet query error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in query_datasheet: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to query datasheet")


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose_system(
    request: DiagnoseRequest,
    ai_service: AIExplanationService = Depends(get_ai_service)
):
    """
    Diagnose system problems from simulation.
    
    Analyzes the simulation results and identifies:
    - Component problems
    - Likely causes
    - Severity levels
    - Critical issues requiring immediate attention
    - Warnings for potential future issues
    
    Provides an overall system health score and actionable insights.
    """
    try:
        result = ai_service.diagnose_system(
            simulation_id=request.simulation_id,
            level=request.level
        )
        return result
    except AIServiceError as e:
        logger.error(f"Diagnose system error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in diagnose_system: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to diagnose system")


@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(
    request: RecommendRequest,
    ai_service: AIExplanationService = Depends(get_ai_service)
):
    """
    Get recommendations for system improvements.
    
    Based on simulation results, provides:
    - Product recommendations (better batteries, inverters, etc.)
    - Configuration changes
    - Expected improvements
    
    Can focus on specific areas (battery, inverter, panels, charge_controller)
    or provide overall recommendations.
    """
    try:
        result = ai_service.get_recommendations(
            simulation_id=request.simulation_id,
            focus_area=request.focus_area,
            level=request.level
        )
        return result
    except AIServiceError as e:
        logger.error(f"Get recommendations error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.get("/health")
async def ai_health_check():
    """
    Check AI service health.
    
    Returns the status of the AI service and available models.
    """
    try:
        from app.services.llm_service import get_llm_service
        
        # Try to get LLM service
        llm = get_llm_service()
        
        return {
            "status": "healthy",
            "model": llm.model,
            "available_models": list(llm.AVAILABLE_MODELS.keys())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "GROQ_API_KEY may not be configured"
        }


@router.get("/context-preview/{simulation_id}")
async def preview_context(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """
    Preview the context data that will be sent to the AI.
    
    Useful for debugging or understanding what data the AI has access to.
    """
    from app.services.context_builder import ContextBuilder
    from app.models.simulation import SimulationHistory
    
    simulation = db.query(SimulationHistory).filter(
        SimulationHistory.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    builder = ContextBuilder(db)
    context = builder.build_full_context(
        simulation_id=simulation_id,
        battery_id=simulation.battery_id,
        inverter_id=simulation.inverter_id,
        panel_id=simulation.panel_id,
        controller_id=simulation.charge_controller_id
    )
    
    # Truncate long text fields for preview
    preview = {
        "simulation_id": context.simulation_summary.get("simulation_id") if context.simulation_summary else simulation_id,
        "timeline_summary": context.timeline_summary,
        "battery": {
            "product_name": context.battery.get("product_name") if context.battery else None,
            "specs_count": len(context.battery.get("specifications", {})) if context.battery else 0,
            "has_datasheet": bool(context.battery.get("datasheet_snippet")) if context.battery else False,
        },
        "inverter": {
            "product_name": context.inverter.get("product_name") if context.inverter else None,
            "specs_count": len(context.inverter.get("specifications", {})) if context.inverter else 0,
        },
        "panel": {
            "product_name": context.panel.get("product_name") if context.panel else None,
            "specs_count": len(context.panel.get("specifications", {})) if context.panel else 0,
        },
        "charge_controller": {
            "product_name": context.charge_controller.get("product_name") if context.charge_controller else None,
            "specs_count": len(context.charge_controller.get("specifications", {})) if context.charge_controller else 0,
        },
        "events_count": len(context.events),
        "datasheet_snippets_count": len(context.datasheet_snippets),
    }
    
    return preview
