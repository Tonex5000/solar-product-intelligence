"""Context Builder Service for AI Explanation Layer."""
import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.specification import ProductSpecification
from app.models.document import Document
from app.models.category import Category
from app.models.simulation import SimulationHistory
from app.schemas.ai import AIContext, DatasheetSnippet, ReferencedSpec, ReferencedEvent

logger = logging.getLogger(__name__)


class ContextBuilder:
    """
    Context Builder Service.
    
    Gathers all relevant data for AI queries from the database.
    """
    
    CATEGORY_NAME_MAP = {
        "battery": "battery",
        "inverter": "inverter",
        "solar_panel": "panel",
        "charge_controller": "charge_controller",
    }
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_product_specs(self, product_id: int) -> list[ProductSpecification]:
        """Get all specifications for a product."""
        return self.db.query(ProductSpecification).filter(
            ProductSpecification.product_id == product_id
        ).all()
    
    def get_product_documents(self, product_id: int) -> list[Document]:
        """Get all documents for a product."""
        return self.db.query(Document).filter(
            Document.product_id == product_id
        ).all()
    
    def specs_to_dict(self, specs: list[ProductSpecification]) -> dict:
        """Convert specifications list to dictionary."""
        return {
            spec.spec_key: {
                "value": spec.spec_value,
                "unit": spec.unit,
                "confidence": spec.confidence_score,
            }
            for spec in specs
        }
    
    def get_simulation(self, simulation_id: int) -> Optional[SimulationHistory]:
        """Get simulation history by ID."""
        return self.db.query(SimulationHistory).filter(
            SimulationHistory.id == simulation_id
        ).first()
    
    def get_simulation_full_results(self, simulation_id: int) -> dict:
        """Get full simulation results from JSON."""
        sim = self.get_simulation(simulation_id)
        if not sim or not sim.full_results_json:
            return {}
        
        try:
            return json.loads(sim.full_results_json)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse simulation results for ID {simulation_id}")
            return {}
    
    def build_battery_context(self, battery_id: int) -> dict:
        """Build context for a battery."""
        product = self.get_product_by_id(battery_id)
        if not product:
            return {}
        
        specs = self.get_product_specs(battery_id)
        documents = self.get_product_documents(battery_id)
        
        # Extract relevant datasheet text
        datasheet_text = ""
        for doc in documents:
            if doc.extracted_text and doc.type.value == "datasheet":
                # Take first 2000 chars
                datasheet_text = doc.extracted_text[:2000]
                break
        
        return {
            "product_id": battery_id,
            "product_name": product.product_name,
            "model_name": product.model_name,
            "company": product.company.name if product.company else "Unknown",
            "specifications": self.specs_to_dict(specs),
            "validation_status": product.validation_status.value,
            "is_verified": product.is_verified,
            "datasheet_snippet": datasheet_text,
        }
    
    def build_inverter_context(self, inverter_id: int) -> dict:
        """Build context for an inverter."""
        product = self.get_product_by_id(inverter_id)
        if not product:
            return {}
        
        specs = self.get_product_specs(inverter_id)
        documents = self.get_product_documents(inverter_id)
        
        datasheet_text = ""
        for doc in documents:
            if doc.extracted_text and doc.type.value == "datasheet":
                datasheet_text = doc.extracted_text[:2000]
                break
        
        return {
            "product_id": inverter_id,
            "product_name": product.product_name,
            "model_name": product.model_name,
            "company": product.company.name if product.company else "Unknown",
            "specifications": self.specs_to_dict(specs),
            "validation_status": product.validation_status.value,
            "is_verified": product.is_verified,
            "datasheet_snippet": datasheet_text,
        }
    
    def build_panel_context(self, panel_id: int) -> dict:
        """Build context for a solar panel."""
        product = self.get_product_by_id(panel_id)
        if not product:
            return {}
        
        specs = self.get_product_specs(panel_id)
        documents = self.get_product_documents(panel_id)
        
        datasheet_text = ""
        for doc in documents:
            if doc.extracted_text and doc.type.value == "datasheet":
                datasheet_text = doc.extracted_text[:2000]
                break
        
        return {
            "product_id": panel_id,
            "product_name": product.product_name,
            "model_name": product.model_name,
            "company": product.company.name if product.company else "Unknown",
            "specifications": self.specs_to_dict(specs),
            "validation_status": product.validation_status.value,
            "is_verified": product.is_verified,
            "datasheet_snippet": datasheet_text,
        }
    
    def build_charge_controller_context(self, controller_id: int) -> dict:
        """Build context for a charge controller."""
        product = self.get_product_by_id(controller_id)
        if not product:
            return {}
        
        specs = self.get_product_specs(controller_id)
        documents = self.get_product_documents(controller_id)
        
        datasheet_text = ""
        for doc in documents:
            if doc.extracted_text and doc.type.value == "datasheet":
                datasheet_text = doc.extracted_text[:2000]
                break
        
        return {
            "product_id": controller_id,
            "product_name": product.product_name,
            "model_name": product.model_name,
            "company": product.company.name if product.company else "Unknown",
            "specifications": self.specs_to_dict(specs),
            "validation_status": product.validation_status.value,
            "is_verified": product.is_verified,
            "datasheet_snippet": datasheet_text,
        }
    
    def build_simulation_context(self, simulation_id: int) -> dict:
        """Build context from simulation results."""
        sim = self.get_simulation(simulation_id)
        if not sim:
            return {}
        
        full_results = self.get_simulation_full_results(simulation_id)
        events = full_results.get("events", [])
        timeline = full_results.get("timeline", [])
        
        # Calculate timeline summary
        if timeline:
            first_entry = timeline[0]
            last_entry = timeline[-1]
            
            # Find days with events
            days_with_events = set()
            for entry in timeline:
                if entry.get("events"):
                    days_with_events.add(entry["day"])
            
            timeline_summary = {
                "simulation_days": len(timeline),
                "first_day": first_entry.get("day", 1),
                "last_day": last_entry.get("day", len(timeline)),
                "days_with_events": len(days_with_events),
                "initial_battery_health": first_entry.get("battery_health", 100),
                "final_battery_health": last_entry.get("battery_health", 0),
                "initial_soc": first_entry.get("battery_soc", 1.0),
                "final_soc": last_entry.get("battery_soc", 0),
            }
        else:
            timeline_summary = {
                "simulation_days": 0,
                "first_day": 0,
                "last_day": 0,
                "days_with_events": 0,
            }
        
        # Parse summary if available
        summary = {}
        if sim.summary_json:
            try:
                summary = json.loads(sim.summary_json)
            except json.JSONDecodeError:
                pass
        
        return {
            "simulation_id": simulation_id,
            "input": {
                "battery_id": sim.battery_id,
                "inverter_id": sim.inverter_id,
                "panel_id": sim.panel_id,
                "charge_controller_id": sim.charge_controller_id,
                "load_watts": sim.load_watts,
                "daily_usage_hours": sim.daily_usage_hours,
                "simulation_days": sim.simulation_days,
                "location": sim.location,
                "avg_sun_hours": sim.avg_sun_hours,
            },
            "summary": summary,
            "events": events,
            "timeline_summary": timeline_summary,
            "created_at": sim.created_at.isoformat() if sim.created_at else None,
        }
    
    def build_full_context(
        self,
        simulation_id: int,
        battery_id: int,
        inverter_id: int,
        panel_id: int,
        controller_id: int
    ) -> AIContext:
        """
        Build complete context for AI queries.
        
        Args:
            simulation_id: Simulation history ID
            battery_id: Battery product ID
            inverter_id: Inverter product ID
            panel_id: Solar panel product ID
            controller_id: Charge controller product ID
            
        Returns:
            AIContext with all relevant data
        """
        simulation_context = self.build_simulation_context(simulation_id)
        
        # Get datasheet snippets for all products
        datasheet_snippets = []
        
        battery_ctx = self.build_battery_context(battery_id)
        if battery_ctx.get("datasheet_snippet"):
            datasheet_snippets.append(DatasheetSnippet(
                product_id=battery_id,
                product_name=battery_ctx.get("product_name", "Unknown"),
                document_type="datasheet",
                snippet=battery_ctx["datasheet_snippet"],
                relevance_score=0.9
            ))
        
        inverter_ctx = self.build_inverter_context(inverter_id)
        if inverter_ctx.get("datasheet_snippet"):
            datasheet_snippets.append(DatasheetSnippet(
                product_id=inverter_id,
                product_name=inverter_ctx.get("product_name", "Unknown"),
                document_type="datasheet",
                snippet=inverter_ctx["datasheet_snippet"],
                relevance_score=0.9
            ))
        
        panel_ctx = self.build_panel_context(panel_id)
        if panel_ctx.get("datasheet_snippet"):
            datasheet_snippets.append(DatasheetSnippet(
                product_id=panel_id,
                product_name=panel_ctx.get("product_name", "Unknown"),
                document_type="datasheet",
                snippet=panel_ctx["datasheet_snippet"],
                relevance_score=0.9
            ))
        
        controller_ctx = self.build_charge_controller_context(controller_id)
        if controller_ctx.get("datasheet_snippet"):
            datasheet_snippets.append(DatasheetSnippet(
                product_id=controller_id,
                product_name=controller_ctx.get("product_name", "Unknown"),
                document_type="datasheet",
                snippet=controller_ctx["datasheet_snippet"],
                relevance_score=0.9
            ))
        
        return AIContext(
            battery=battery_ctx,
            inverter=inverter_ctx,
            panel=panel_ctx,
            charge_controller=controller_ctx,
            events=simulation_context.get("events", []),
            timeline_summary=simulation_context.get("timeline_summary", {}),
            datasheet_snippets=datasheet_snippets,
            simulation_input=simulation_context.get("input", {}),
            simulation_summary=simulation_context.get("summary", {}),
        )
    
    def build_product_context(self, product_id: int) -> dict:
        """Build context for a single product."""
        product = self.get_product_by_id(product_id)
        if not product:
            return {}
        
        specs = self.get_product_specs(product_id)
        documents = self.get_product_documents(product_id)
        category_name = product.category.name if product.category else "unknown"
        
        # Get all datasheet text
        datasheet_texts = []
        for doc in documents:
            if doc.extracted_text:
                datasheet_texts.append({
                    "type": doc.type.value,
                    "text": doc.extracted_text[:3000],  # Limit to 3000 chars
                })
        
        return {
            "product_id": product_id,
            "product_name": product.product_name,
            "model_name": product.model_name,
            "company": product.company.name if product.company else "Unknown",
            "category": category_name,
            "specifications": self.specs_to_dict(specs),
            "documents": datasheet_texts,
            "validation_status": product.validation_status.value,
            "is_verified": product.is_verified,
        }
    
    def search_datasheet(
        self,
        product_id: int,
        keywords: list[str],
        max_snippets: int = 3
    ) -> list[DatasheetSnippet]:
        """
        Search for relevant snippets in product datasheet.
        
        Args:
            product_id: Product ID to search
            keywords: Keywords to search for
            max_snippets: Maximum number of snippets to return
            
        Returns:
            List of relevant DatasheetSnippet
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return []
        
        snippets = []
        documents = self.get_product_documents(product_id)
        
        for doc in documents:
            if not doc.extracted_text:
                continue
            
            text = doc.extracted_text.lower()
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in text:
                    # Find context around the keyword
                    idx = text.find(keyword_lower)
                    start = max(0, idx - 100)
                    end = min(len(text), idx + len(keyword) + 200)
                    snippet_text = doc.extracted_text[start:end]
                    
                    # Calculate relevance (simple keyword match count)
                    relevance = sum(1 for k in keywords if k.lower() in text) / len(keywords)
                    
                    snippets.append(DatasheetSnippet(
                        product_id=product_id,
                        product_name=product.product_name,
                        document_type=doc.type.value,
                        snippet=snippet_text,
                        relevance_score=relevance
                    ))
                    break  # Only one snippet per keyword per document
        
        # Sort by relevance and limit
        snippets.sort(key=lambda x: x.relevance_score, reverse=True)
        return snippets[:max_snippets]
