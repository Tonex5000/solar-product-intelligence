"""AI Explanation Service - Main service for AI queries."""
import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.schemas.ai import (
    ExplanationLevel,
    ExplainSimulationResponse,
    DatasheetQueryResponse,
    DiagnoseResponse,
    RecommendResponse,
    ReferencedSpec,
    ReferencedEvent,
    DiagnosisProblem,
    DiagnosisSeverity,
    ProductRecommendation,
    DatasheetSnippet,
)
from app.services.llm_service import LLMService, LLMServiceError, get_llm_service
from app.services.context_builder import ContextBuilder
from app.services.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Exception for AI service errors."""
    pass


class AIExplanationService:
    """
    Main AI Explanation Service.
    
    Provides explanations, diagnoses, and recommendations for solar systems.
    """
    
    def __init__(
        self,
        db: Session,
        llm_service: Optional[LLMService] = None
    ):
        """
        Initialize AI service.
        
        Args:
            db: Database session
            llm_service: Optional LLM service instance (uses default if not provided)
        """
        self.db = db
        self.context_builder = ContextBuilder(db)
        self.prompt_templates = PromptTemplates()
        self.llm = llm_service or get_llm_service()
    
    def _extract_referenced_specs(self, context) -> list[ReferencedSpec]:
        """Extract referenced specs from context."""
        specs = []
        
        # Battery specs
        battery = getattr(context, 'battery', {}) or {}
        if battery.get('specifications'):
            for key, value in battery['specifications'].items():
                if isinstance(value, dict):
                    specs.append(ReferencedSpec(
                        product_id=battery.get('product_id', 0),
                        product_name=battery.get('product_name', 'Unknown'),
                        spec_key=key,
                        spec_value=str(value.get('value', 'N/A')),
                        unit=value.get('unit')
                    ))
        
        # Inverter specs
        inverter = getattr(context, 'inverter', {}) or {}
        if inverter.get('specifications'):
            for key, value in inverter['specifications'].items():
                if isinstance(value, dict):
                    specs.append(ReferencedSpec(
                        product_id=inverter.get('product_id', 0),
                        product_name=inverter.get('product_name', 'Unknown'),
                        spec_key=key,
                        spec_value=str(value.get('value', 'N/A')),
                        unit=value.get('unit')
                    ))
        
        # Panel specs
        panel = getattr(context, 'panel', {}) or {}
        if panel.get('specifications'):
            for key, value in panel['specifications'].items():
                if isinstance(value, dict):
                    specs.append(ReferencedSpec(
                        product_id=panel.get('product_id', 0),
                        product_name=panel.get('product_name', 'Unknown'),
                        spec_key=key,
                        spec_value=str(value.get('value', 'N/A')),
                        unit=value.get('unit')
                    ))
        
        # Controller specs
        controller = getattr(context, 'charge_controller', {}) or {}
        if controller.get('specifications'):
            for key, value in controller['specifications'].items():
                if isinstance(value, dict):
                    specs.append(ReferencedSpec(
                        product_id=controller.get('product_id', 0),
                        product_name=controller.get('product_name', 'Unknown'),
                        spec_key=key,
                        spec_value=str(value.get('value', 'N/A')),
                        unit=value.get('unit')
                    ))
        
        return specs
    
    def _extract_referenced_events(self, context) -> list[ReferencedEvent]:
        """Extract referenced events from context."""
        events = []
        
        for event in (getattr(context, 'events', []) or [])[:20]:
            events.append(ReferencedEvent(
                day=event.get('day', 0),
                event_type=event.get('type', 'unknown'),
                message=event.get('message', ''),
                severity=event.get('severity', 'low')
            ))
        
        return events
    
    def explain_simulation(
        self,
        simulation_id: int,
        question: str,
        level: ExplanationLevel = ExplanationLevel.INTERMEDIATE
    ) -> ExplainSimulationResponse:
        """
        Explain a simulation outcome.
        
        Args:
            simulation_id: Simulation history ID
            question: User's question
            level: Explanation level (beginner, intermediate, engineer)
            
        Returns:
            Explanation response with references
        """
        # Get simulation
        simulation = self.context_builder.get_simulation(simulation_id)
        if not simulation:
            raise AIServiceError(f"Simulation {simulation_id} not found")
        
        # Build context
        context = self.context_builder.build_full_context(
            simulation_id=simulation_id,
            battery_id=simulation.battery_id,
            inverter_id=simulation.inverter_id,
            panel_id=simulation.panel_id,
            controller_id=simulation.charge_controller_id
        )
        
        # Build context string
        context_str = self.prompt_templates.build_simulation_explanation_context(
            context=context,
            question=question,
            level=level
        )
        
        # Get system prompt
        system_prompt = self.prompt_templates.get_system_prompt(level)
        
        # User message
        user_message = f"""Question: {question}

Answer the question based ONLY on the simulation data and product specifications provided above."""

        try:
            # Generate explanation
            answer = self.llm.generate_explanation(
                system_prompt=system_prompt,
                context=context_str,
                question=user_message
            )
            
            # Check if answer indicates no data found
            information_found = "not available" not in answer.lower() and "not found" not in answer.lower()
            
            # Calculate confidence based on how much context was used
            confidence = 0.9 if len(context.events) > 0 else 0.7
            
            return ExplainSimulationResponse(
                answer=answer,
                key_factors=self._extract_key_factors(answer),
                referenced_specs=self._extract_referenced_specs(context),
                events_used=self._extract_referenced_events(context),
                confidence=confidence
            )
            
        except LLMServiceError as e:
            logger.error(f"LLM service error: {e}")
            raise AIServiceError(f"Failed to generate explanation: {str(e)}")
    
    def query_datasheet(
        self,
        product_id: int,
        question: str,
        level: ExplanationLevel = ExplanationLevel.INTERMEDIATE
    ) -> DatasheetQueryResponse:
        """
        Query a product's datasheet.
        
        Args:
            product_id: Product ID
            question: User's question
            level: Explanation level
            
        Returns:
            Datasheet query response
        """
        # Build product context
        product_context = self.context_builder.build_product_context(product_id)
        
        if not product_context:
            raise AIServiceError(f"Product {product_id} not found")
        
        # Build context string
        context_str = self.prompt_templates.build_datasheet_query_context(
            product_context=product_context,
            question=question
        )
        
        # Get system prompt
        system_prompt = self.prompt_templates.get_system_prompt(level)
        
        # User message
        user_message = f"""Question: {question}

Answer based ONLY on the product information and datasheet content provided above."""

        try:
            answer = self.llm.generate_explanation(
                system_prompt=system_prompt,
                context=context_str,
                question=user_message
            )
            
            # Check if information was found
            information_found = "not available" not in answer.lower() and "not found" not in answer.lower()
            
            # Extract snippets
            snippets = []
            for doc in product_context.get('documents', []):
                if doc.get('text'):
                    snippets.append(DatasheetSnippet(
                        product_id=product_id,
                        product_name=product_context.get('product_name', 'Unknown'),
                        document_type=doc.get('type', 'unknown'),
                        snippet=doc.get('text', '')[:500],
                        relevance_score=0.8
                    ))
            
            return DatasheetQueryResponse(
                answer=answer,
                snippets=snippets,
                referenced_specs=self._extract_referenced_specs(type('obj', (object,), {'battery': product_context})()),
                confidence=0.9 if information_found else 0.5,
                information_found=information_found
            )
            
        except LLMServiceError as e:
            logger.error(f"LLM service error: {e}")
            raise AIServiceError(f"Failed to query datasheet: {str(e)}")
    
    def diagnose_system(
        self,
        simulation_id: int,
        level: ExplanationLevel = ExplanationLevel.INTERMEDIATE
    ) -> DiagnoseResponse:
        """
        Diagnose system problems from simulation.
        
        Args:
            simulation_id: Simulation history ID
            level: Explanation level
            
        Returns:
            Diagnosis response with problems
        """
        # Get simulation
        simulation = self.context_builder.get_simulation(simulation_id)
        if not simulation:
            raise AIServiceError(f"Simulation {simulation_id} not found")
        
        # Build context
        context = self.context_builder.build_full_context(
            simulation_id=simulation_id,
            battery_id=simulation.battery_id,
            inverter_id=simulation.inverter_id,
            panel_id=simulation.panel_id,
            controller_id=simulation.charge_controller_id
        )
        
        # Build diagnosis context
        context_str = self.prompt_templates.build_diagnosis_context(context)
        
        # Get system prompt
        system_prompt = self.prompt_templates.get_system_prompt(level)
        
        # Special diagnosis prompt
        diagnosis_prompt = f"""{system_prompt}

DIAGNOSIS TASK:
Analyze the simulation data and identify all problems with the solar system.
For each problem, identify:
1. The affected component
2. The nature of the problem
3. The likely cause
4. Severity level (LOW, MEDIUM, HIGH, CRITICAL)

Format your response as a JSON object:
{{
    "summary": "Overall diagnosis summary in 2-3 sentences",
    "problems": [
        {{
            "component": "affected component name",
            "problem": "description of the problem",
            "cause": "likely cause of the problem",
            "severity": "LOW|MEDIUM|HIGH|CRITICAL"
        }}
    ],
    "overall_health_score": 0-100,
    "critical_issues": ["list of critical issue descriptions"],
    "warnings": ["list of warning descriptions"]
}}"""

        try:
            # Generate diagnosis
            response = self.llm.structured_chat(
                system_prompt=diagnosis_prompt,
                user_message=f"Diagnose the solar system based on this data:\n\n{context_str}",
                response_schema={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "problems": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "component": {"type": "string"},
                                    "problem": {"type": "string"},
                                    "cause": {"type": "string"},
                                    "severity": {"type": "string"}
                                }
                            }
                        },
                        "overall_health_score": {"type": "number"},
                        "critical_issues": {"type": "array", "items": {"type": "string"}},
                        "warnings": {"type": "array", "items": {"type": "string"}}
                    }
                }
            )
            
            # Parse response
            problems = []
            for p in response.get('problems', []):
                severity_str = p.get('severity', 'MEDIUM').upper()
                try:
                    severity = DiagnosisSeverity(severity_str)
                except ValueError:
                    severity = DiagnosisSeverity.MEDIUM
                
                problems.append(DiagnosisProblem(
                    component=p.get('component', 'Unknown'),
                    problem=p.get('problem', ''),
                    cause=p.get('cause', ''),
                    severity=severity,
                    evidence=[]
                ))
            
            return DiagnoseResponse(
                summary=response.get('summary', 'Unable to generate diagnosis'),
                problems=problems,
                overall_health_score=response.get('overall_health_score', 50),
                critical_issues=response.get('critical_issues', []),
                warnings=response.get('warnings', []),
                confidence=0.85
            )
            
        except (LLMServiceError, json.JSONDecodeError) as e:
            logger.error(f"Diagnosis error: {e}")
            # Fallback to basic diagnosis
            return self._basic_diagnosis(context)
    
    def _basic_diagnosis(self, context) -> DiagnoseResponse:
        """Basic diagnosis when LLM fails."""
        summary = context.simulation_summary
        events = context.events
        
        problems = []
        warnings = []
        critical_issues = []
        
        if summary:
            # Battery health
            health = summary.get('battery_health_final', 100)
            if health < 20:
                problems.append(DiagnosisProblem(
                    component="battery",
                    problem="Battery health critically low",
                    cause="Excessive depth of discharge or overcurrent",
                    severity=DiagnosisSeverity.CRITICAL,
                    evidence=[f"Final health: {health}%"]
                ))
                critical_issues.append(f"Battery health at {health}%")
            elif health < 50:
                problems.append(DiagnosisProblem(
                    component="battery",
                    problem="Battery health degraded",
                    cause="Operating conditions outside optimal range",
                    severity=DiagnosisSeverity.HIGH,
                    evidence=[f"Final health: {health}%"]
                ))
                warnings.append(f"Battery health degraded to {health}%")
            
            # Failures
            failures = summary.get('system_failures', 0)
            if failures > 0:
                critical_issues.append(f"{failures} system failures occurred")
        
        # Event-based analysis
        damage_events = [e for e in events if e.get('type') == 'damage']
        if len(damage_events) > 10:
            warnings.append(f"{len(damage_events)} damage events recorded")
        
        overall_health = summary.get('battery_health_final', 100) if summary else 50
        
        return DiagnoseResponse(
            summary=f"System health score: {overall_health}%. {'Issues detected.' if problems else 'System operating within acceptable parameters.'}",
            problems=problems,
            overall_health_score=overall_health,
            critical_issues=critical_issues,
            warnings=warnings,
            confidence=0.6
        )
    
    def get_recommendations(
        self,
        simulation_id: int,
        focus_area: Optional[str] = None,
        level: ExplanationLevel = ExplanationLevel.INTERMEDIATE
    ) -> RecommendResponse:
        """
        Get recommendations for system improvements.
        
        Args:
            simulation_id: Simulation history ID
            focus_area: Optional focus on specific component
            level: Explanation level
            
        Returns:
            Recommendations response
        """
        # Get simulation
        simulation = self.context_builder.get_simulation(simulation_id)
        if not simulation:
            raise AIServiceError(f"Simulation {simulation_id} not found")
        
        # Build context
        context = self.context_builder.build_full_context(
            simulation_id=simulation_id,
            battery_id=simulation.battery_id,
            inverter_id=simulation.inverter_id,
            panel_id=simulation.panel_id,
            controller_id=simulation.charge_controller_id
        )
        
        # Build recommendation context
        context_str = self.prompt_templates.build_recommendation_context(
            context=context,
            focus_area=focus_area
        )
        
        # Get system prompt
        system_prompt = self.prompt_templates.get_system_prompt(level)
        
        # Recommendation prompt
        rec_prompt = f"""{system_prompt}

RECOMMENDATION TASK:
Based on the simulation data and current system configuration, provide actionable recommendations to improve system performance, longevity, or reliability.

For each recommendation, explain:
1. What should be changed
2. Why this change helps
3. Expected improvement

Format your response as JSON:
{{
    "summary": "Overall recommendation summary",
    "product_recommendations": [
        {{
            "category": "battery|inverter|panel|charge_controller",
            "product_id": null,
            "product_name": null,
            "reason": "why this product would be better",
            "expected_improvement": "what improvement to expect",
            "priority": "HIGH|MEDIUM|LOW"
        }}
    ],
    "configuration_changes": [
        "specific configuration change description"
    ],
    "reasoning": "detailed technical reasoning"
}}"""

        try:
            response = self.llm.structured_chat(
                system_prompt=rec_prompt,
                user_message=f"Generate recommendations for this solar system:\n\n{context_str}",
                response_schema={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "product_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string"},
                                    "product_id": {"type": ["number", "null"]},
                                    "product_name": {"type": ["string", "null"]},
                                    "reason": {"type": "string"},
                                    "expected_improvement": {"type": "string"},
                                    "priority": {"type": "string"}
                                }
                            }
                        },
                        "configuration_changes": {"type": "array", "items": {"type": "string"}},
                        "reasoning": {"type": "string"}
                    }
                }
            )
            
            # Parse recommendations
            recommendations = []
            for rec in response.get('product_recommendations', []):
                recommendations.append(ProductRecommendation(
                    category=rec.get('category', 'system'),
                    product_id=rec.get('product_id'),
                    product_name=rec.get('product_name'),
                    reason=rec.get('reason', ''),
                    expected_improvement=rec.get('expected_improvement', ''),
                    priority=rec.get('priority', 'MEDIUM')
                ))
            
            return RecommendResponse(
                summary=response.get('summary', 'No recommendations available'),
                product_recommendations=recommendations,
                configuration_changes=response.get('configuration_changes', []),
                reasoning=response.get('reasoning', ''),
                confidence=0.8
            )
            
        except (LLMServiceError, json.JSONDecodeError) as e:
            logger.error(f"Recommendation error: {e}")
            return self._basic_recommendations(context)
    
    def _basic_recommendations(self, context) -> RecommendResponse:
        """Basic recommendations when LLM fails."""
        summary = context.simulation_summary
        recommendations = []
        config_changes = []
        
        if summary:
            health = summary.get('battery_health_final', 100)
            
            if health < 50:
                recommendations.append(ProductRecommendation(
                    category="battery",
                    reason="Battery health degraded - consider upgrading",
                    expected_improvement="Improved longevity and reliability",
                    priority="HIGH"
                ))
                config_changes.append("Reduce daily depth of discharge to below 50%")
            
            max_load = summary.get('max_inverter_load_percent', 0)
            if max_load > 90:
                recommendations.append(ProductRecommendation(
                    category="inverter",
                    reason="Inverter operating near capacity",
                    expected_improvement="Better efficiency and reduced failure risk",
                    priority="HIGH" if max_load > 100 else "MEDIUM"
                ))
                config_changes.append(f"Upgrade inverter or reduce peak load (current peak: {max_load}%)")
        
        return RecommendResponse(
            summary="Basic recommendations generated from simulation data.",
            product_recommendations=recommendations,
            configuration_changes=config_changes,
            reasoning="Recommendations based on observed simulation issues.",
            confidence=0.5
        )
    
    def _extract_key_factors(self, answer: str) -> list[str]:
        """Extract key factors from answer text."""
        # Simple heuristic: look for bullet points or numbered items
        factors = []
        
        lines = answer.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                # Extract text after bullet
                factor = line.lstrip('-*•').strip()
                if len(factor) > 10:  # Filter short items
                    factors.append(factor)
            elif line and line[0].isdigit() and '.' in line[:3]:
                # Numbered item
                if len(line) > 10:
                    factors.append(line)
        
        return factors[:5]  # Limit to 5 factors
