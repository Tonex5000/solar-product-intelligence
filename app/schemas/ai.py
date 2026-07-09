"""Pydantic schemas for AI Explanation Layer."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ExplanationLevel(str, Enum):
    """Explanation detail levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ENGINEER = "engineer"


class DiagnosisSeverity(str, Enum):
    """Problem severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReferencedSpec(BaseModel):
    """Reference to a specification."""
    product_id: int
    product_name: str
    spec_key: str
    spec_value: str
    unit: Optional[str] = None


class ReferencedEvent(BaseModel):
    """Reference to a simulation event."""
    day: int
    event_type: str
    message: str
    severity: str


class DiagnosisProblem(BaseModel):
    """Detected problem in system."""
    component: str
    problem: str
    cause: str
    severity: DiagnosisSeverity
    evidence: list[str] = Field(default_factory=list)


class ProductRecommendation(BaseModel):
    """Product recommendation with reasoning."""
    category: str
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    reason: str
    expected_improvement: str
    priority: str


class DatasheetSnippet(BaseModel):
    """Snippet from datasheet with context."""
    product_id: int
    product_name: str
    document_type: str
    snippet: str
    relevance_score: float = Field(ge=0, le=1)


class ExplainSimulationRequest(BaseModel):
    """Request to explain simulation outcome."""
    simulation_id: int = Field(..., description="Simulation ID to explain")
    question: str = Field(..., description="User's question about the simulation")
    level: ExplanationLevel = Field(
        ExplanationLevel.INTERMEDIATE,
        description="Explanation detail level"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "simulation_id": 1,
                "question": "Why did the battery degrade so fast?",
                "level": "intermediate"
            }
        }
    )


class ExplainSimulationResponse(BaseModel):
    """Response with explanation."""
    answer: str = Field(..., description="AI-generated explanation")
    key_factors: list[str] = Field(default_factory=list, description="Key factors identified")
    referenced_specs: list[ReferencedSpec] = Field(default_factory=list)
    events_used: list[ReferencedEvent] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, description="Confidence in the answer")


class DatasheetQueryRequest(BaseModel):
    """Request to query a product datasheet."""
    product_id: int = Field(..., description="Product ID to query")
    question: str = Field(..., description="Question about the product")
    level: ExplanationLevel = Field(
        ExplanationLevel.INTERMEDIATE,
        description="Explanation detail level"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "question": "What is the max discharge current?",
                "level": "engineer"
            }
        }
    )


class DatasheetQueryResponse(BaseModel):
    """Response with datasheet answer."""
    answer: str = Field(..., description="AI-generated answer from datasheet")
    snippets: list[DatasheetSnippet] = Field(default_factory=list)
    referenced_specs: list[ReferencedSpec] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    information_found: bool = Field(..., description="Whether information was found")


class DiagnoseRequest(BaseModel):
    """Request to diagnose simulation problems."""
    simulation_id: int = Field(..., description="Simulation ID to diagnose")
    level: ExplanationLevel = Field(
        ExplanationLevel.INTERMEDIATE,
        description="Explanation detail level"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "simulation_id": 1,
                "level": "engineer"
            }
        }
    )


class DiagnoseResponse(BaseModel):
    """Response with system diagnosis."""
    summary: str = Field(..., description="Overall diagnosis summary")
    problems: list[DiagnosisProblem] = Field(default_factory=list)
    overall_health_score: float = Field(ge=0, le=100, description="System health 0-100")
    critical_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class RecommendRequest(BaseModel):
    """Request for product/configuration recommendations."""
    simulation_id: int = Field(..., description="Simulation ID to base recommendations on")
    focus_area: Optional[str] = Field(
        None,
        description="Focus on specific area: battery, inverter, panels, charge_controller"
    )
    level: ExplanationLevel = Field(
        ExplanationLevel.INTERMEDIATE,
        description="Explanation detail level"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "simulation_id": 1,
                "focus_area": "battery",
                "level": "intermediate"
            }
        }
    )


class RecommendResponse(BaseModel):
    """Response with recommendations."""
    summary: str = Field(..., description="Recommendation summary")
    product_recommendations: list[ProductRecommendation] = Field(default_factory=list)
    configuration_changes: list[str] = Field(default_factory=list)
    reasoning: str = Field(..., description="Detailed reasoning")
    confidence: float = Field(ge=0, le=1)


class AIContext(BaseModel):
    """Context data for AI queries."""
    battery: dict = Field(default_factory=dict)
    inverter: dict = Field(default_factory=dict)
    panel: dict = Field(default_factory=dict)
    charge_controller: dict = Field(default_factory=dict)
    events: list[dict] = Field(default_factory=list)
    timeline_summary: dict = Field(default_factory=dict)
    datasheet_snippets: list[DatasheetSnippet] = Field(default_factory=list)
    simulation_input: dict = Field(default_factory=dict)
    simulation_summary: dict = Field(default_factory=dict)


class SystemPromptTemplate(BaseModel):
    """Template for system prompts."""
    level: ExplanationLevel
    role: str
    rules: list[str]
    output_format: str


# System prompts for different explanation levels
SYSTEM_PROMPTS = {
    ExplanationLevel.BEGINNER: SystemPromptTemplate(
        level=ExplanationLevel.BEGINNER,
        role="""You are a friendly solar energy expert explaining concepts to someone 
who is new to solar technology. Use simple language, avoid jargon, and provide 
clear analogies to everyday situations.""",
        rules=[
            "Use simple, everyday language",
            "Avoid technical jargon or explain it when necessary",
            "Use analogies to common experiences",
            "Focus on what matters to the user practically",
            "Be encouraging and supportive",
            "Only use information provided in the context data",
            "If information is not available, say 'I don't have that information from the provided data'",
        ],
        output_format="""Provide a friendly, easy-to-understand explanation.
Break down complex concepts simply.
End with practical next steps if applicable."""
    ),
    ExplanationLevel.INTERMEDIATE: SystemPromptTemplate(
        level=ExplanationLevel.INTERMEDIATE,
        role="""You are a knowledgeable solar engineer explaining concepts to someone 
who has basic understanding of solar systems but wants more technical detail.""",
        rules=[
            "Use appropriate technical terminology",
            "Explain key technical concepts clearly",
            "Reference specific specs and data points",
            "Provide cause-and-effect explanations",
            "Be precise but not overly technical",
            "Only use information provided in the context data",
            "If information is not available, say 'This information is not available in the provided data'",
        ],
        output_format="""Provide a balanced explanation with technical context.
Include relevant specifications and data.
Explain the reasoning behind observations."""
    ),
    ExplanationLevel.ENGINEER: SystemPromptTemplate(
        level=ExplanationLevel.ENGINEER,
        role="""You are a senior solar systems engineer providing detailed technical analysis.
You are addressing a professional with deep knowledge of electrical systems, 
battery technology, and solar installations.""",
        rules=[
            "Use precise engineering terminology",
            "Reference specific datasheet values and specifications",
            "Include detailed technical analysis",
            "Discuss efficiency losses, degradation mechanisms, and failure modes",
            "Provide quantitative analysis where possible",
            "Only use information provided in the context data",
            "If information is not available, clearly state 'DATA NOT AVAILABLE: [specific info missing]'",
        ],
        output_format="""Provide comprehensive technical analysis.
Include all relevant specifications with units.
Discuss engineering tradeoffs and design considerations.
Reference specific failure modes and degradation mechanisms."""
    ),
}
