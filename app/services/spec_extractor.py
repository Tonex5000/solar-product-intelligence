"""Rule-based specification extraction from text."""
import logging
import re
from typing import Optional

from sqlalchemy.orm import Session

from app.models.specification import ProductSpecification
from app.models.product import Product

logger = logging.getLogger(__name__)


class SpecExtractor:
    """Service for extracting specifications from document text using regex patterns."""

    # Regex patterns for common solar product specifications
    SPEC_PATTERNS = {
        # Voltage patterns
        "voltage": [
            r"(?:nominal\s+)?voltage[:\s]+([0-9.]+)\s*[vV]",
            r"([0-9.]+)\s*[vV]\s*(?:nominal)",
            r"system\s+voltage[:\s]+([0-9.]+)\s*[vV]",
        ],
        "battery_voltage_range": [
            r"battery\s+voltage\s+range[:\s]+([0-9.]+)\s*[-–]\s*([0-9.]+)\s*[vV]",
            r"([0-9.]+)\s*[-–]\s*([0-9.]+)\s*[vV]\s*battery\s+range",
        ],
        
        # Current patterns
        "current": [
            r"(?:max(?:imum)?\s+)?(?:output\s+)?current[:\s]+([0-9.]+)\s*[aA]",
            r"rated\s+current[:\s]+([0-9.]+)\s*[aA]",
            r"([0-9.]+)\s*[aA]\s*(?:max|rated)",
        ],
        "max_charge_current": [
            r"max(?:imum)?\s+charge\s+current[:\s]+([0-9.]+)\s*[aA]",
            r"charge\s+current[:\s]+([0-9.]+)\s*[aA]",
            r"([0-9.]+)\s*[aA]\s*max\s+charge",
        ],
        "Isc": [
            r"Isc[:\s]+([0-9.]+)\s*[aA]",
            r"short\s+circuit\s+current[:\s]+([0-9.]+)\s*[aA]",
        ],
        
        # Power patterns
        "rated_power": [
            r"rated\s+power[:\s]+([0-9.]+)\s*[wWkK][wW]?",
            r"([0-9.]+)\s*[kK][wW]\s*rated",
            r"nominal\s+power[:\s]+([0-9.]+)\s*[wWkK][wW]?",
        ],
        "wattage": [
            r"([0-9.]+)\s*[wW][pP]?\s*(?:peak)?",
            r"wattage[:\s]+([0-9.]+)\s*[wW]",
            r"power\s+output[:\s]+([0-9.]+)\s*[wWkK][wW]?",
        ],
        
        # Capacity patterns
        "capacity": [
            r"capacity[:\s]+([0-9.]+)\s*[aAhH]",
            r"([0-9.]+)\s*[aAhH]\s*@?\s*(?:20h?|C20)",
            r"rated\s+capacity[:\s]+([0-9.]+)\s*[aAhH]",
        ],
        
        # Efficiency patterns
        "efficiency": [
            r"efficiency[:\s]+([0-9.]+)\s*%",
            r"peak\s+efficiency[:\s]+([0-9.]+)\s*%",
            r"([0-9.]+)\s*%\s*efficiency",
        ],
        
        # Voltage specifications for panels
        "Voc": [
            r"Voc[:\s]+([0-9.]+)\s*[vV]",
            r"open\s+circuit\s+voltage[:\s]+([0-9.]+)\s*[vV]",
            r"Voc\s*\(?\s*STC\s*\)?[:\s]+([0-9.]+)\s*[vV]",
        ],
        "Vmp": [
            r"Vmp[:\s]+([0-9.]+)\s*[vV]",
            r"maximum\s+power\s+voltage[:\s]+([0-9.]+)\s*[vV]",
        ],
        "max_input_voltage": [
            r"max(?:imum)?\s+input\s+voltage[:\s]+([0-9.]+)\s*[vV]",
            r"PV\s+max\s+voltage[:\s]+([0-9.]+)\s*[vV]",
            r"([0-9.]+)\s*[vV]\s*max\s+input",
        ],
        
        # Cycle life
        "cycle_life": [
            r"cycle\s+life[:\s]+([0-9,]+)\s*(?:cycles?)?",
            r"([0-9,]+)\s*cycles?\s*(?:@?\s*DOD)?",
            r"@?\s*([0-9]+)%\s*DOD[:\s]+([0-9,]+)\s*cycles?",
        ],
    }

    # Units mapping
    UNIT_MAPPING = {
        "voltage": "V",
        "battery_voltage_range": "V",
        "current": "A",
        "max_charge_current": "A",
        "Isc": "A",
        "rated_power": "W",
        "wattage": "W",
        "capacity": "Ah",
        "efficiency": "%",
        "Voc": "V",
        "Vmp": "V",
        "max_input_voltage": "V",
        "cycle_life": "cycles",
    }

    def __init__(self, db: Session):
        """Initialize the spec extractor with a database session."""
        self.db = db

    def extract_specs_from_text(self, text: str) -> dict[str, dict]:
        """
        Extract specifications from text using regex patterns.

        Args:
            text: Document text to parse

        Returns:
            Dictionary mapping spec_key to {'value': str, 'confidence': float, 'source': str}
        """
        extracted = {}
        
        for spec_key, patterns in self.SPEC_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1) if match.lastindex else match.group(0)
                    
                    # Clean up the value
                    value = value.strip()
                    
                    # Calculate confidence based on pattern specificity
                    confidence = 0.7  # Base confidence
                    if "rated" in pattern.lower():
                        confidence += 0.1
                    if "maximum" in pattern.lower():
                        confidence += 0.05
                    confidence = min(confidence, 1.0)
                    
                    # Find source location
                    source = self._find_source_line(text, match.group(0))
                    
                    extracted[spec_key] = {
                        "value": value,
                        "confidence": confidence,
                        "source": source,
                    }
                    break  # Use first matching pattern
        
        return extracted

    def _find_source_line(self, text: str, search_str: str) -> str:
        """Find the line containing the search string."""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if search_str in line:
                return f"Line {i + 1}"
        return "Unknown"

    def store_specifications(
        self,
        product_id: int,
        specifications: dict[str, dict]
    ) -> list[ProductSpecification]:
        """
        Store extracted specifications in the database.

        Args:
            product_id: ID of the product
            specifications: Dictionary of extracted specs

        Returns:
            List of created ProductSpecification objects
        """
        created_specs = []
        
        for spec_key, spec_data in specifications.items():
            spec = ProductSpecification(
                product_id=product_id,
                spec_key=spec_key,
                spec_value=spec_data["value"],
                unit=self.UNIT_MAPPING.get(spec_key),
                confidence_score=spec_data["confidence"],
                source_location=spec_data.get("source"),
            )
            self.db.add(spec)
            created_specs.append(spec)
        
        self.db.commit()
        
        # Refresh to get IDs
        for spec in created_specs:
            self.db.refresh(spec)
        
        return created_specs

    def extract_and_store(self, product_id: int, text: str) -> list[ProductSpecification]:
        """
        Extract specifications from text and store them.

        Args:
            product_id: ID of the product
            text: Document text to parse

        Returns:
            List of created ProductSpecification objects
        """
        # First, clear existing specs for this product
        self.db.query(ProductSpecification).filter(
            ProductSpecification.product_id == product_id
        ).delete()
        self.db.commit()
        
        # Extract new specs
        specifications = self.extract_specs_from_text(text)
        
        # Store specs
        return self.store_specifications(product_id, specifications)

    def get_extraction_summary(self, specifications: dict[str, dict]) -> dict:
        """Get a summary of extracted specifications."""
        return {
            "total_specs": len(specifications),
            "by_category": self._categorize_specs(specifications),
            "average_confidence": sum(s["confidence"] for s in specifications.values()) / len(specifications) if specifications else 0,
        }

    def _categorize_specs(self, specifications: dict[str, dict]) -> dict:
        """Categorize specifications by type."""
        categories = {
            "electrical": ["voltage", "battery_voltage_range", "max_input_voltage", "Voc", "Vmp"],
            "current": ["current", "max_charge_current", "Isc"],
            "power": ["rated_power", "wattage"],
            "capacity": ["capacity"],
            "performance": ["efficiency", "cycle_life"],
        }
        
        result = {}
        for category, keys in categories.items():
            matching = {k: specifications[k] for k in keys if k in specifications}
            if matching:
                result[category] = matching
        
        return result
