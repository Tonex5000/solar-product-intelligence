"""Product validation engine for enforcing data integrity rules."""
import logging
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.models.product import Product, ValidationStatus
from app.models.document import Document, DocumentType, ExtractionStatus
from app.models.specification import ProductSpecification, REQUIRED_SPECS_BY_CATEGORY
from app.models.category import Category

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of product validation."""
    is_valid: bool
    validation_status: ValidationStatus
    errors: list[str]
    warnings: list[str]
    checked_rules: dict[str, bool]


class ValidationEngine:
    """
    Validation engine for enforcing strict data integrity rules.

    Rules:
    1. Product MUST have a datasheet document
    2. Datasheet extraction MUST be successful
    3. Product MUST contain minimum required specs based on category
    """

    def __init__(self, db: Session):
        """Initialize the validation engine with a database session."""
        self.db = db

    def validate_product(self, product_id: int) -> ValidationResult:
        """
        Validate a product against all business rules.

        Args:
            product_id: ID of the product to validate

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        product = self.db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return ValidationResult(
                is_valid=False,
                validation_status=ValidationStatus.REJECTED,
                errors=["Product not found"],
                warnings=[],
                checked_rules={},
            )
        
        errors = []
        warnings = []
        checked_rules = {}
        
        # Rule 1: Check datasheet exists
        has_datasheet, datasheet_error = self._check_datasheet_exists(product_id)
        checked_rules["has_datasheet"] = has_datasheet
        if not has_datasheet:
            errors.append(f"Datasheet requirement failed: {datasheet_error}")
        
        # Rule 2: Check extraction status
        extraction_success, extraction_error = self._check_extraction_status(product_id)
        checked_rules["extraction_successful"] = extraction_success
        if not extraction_success:
            errors.append(f"Extraction requirement failed: {extraction_error}")
        
        # Rule 3: Check required specifications
        specs_complete, specs_errors, specs_warnings = self._check_required_specs(
            product_id,
            product.category.name if product.category else None
        )
        checked_rules["required_specs_present"] = specs_complete
        errors.extend(specs_errors)
        warnings.extend(specs_warnings)
        
        # Determine validation status
        is_valid = len(errors) == 0
        validation_status = (
            ValidationStatus.APPROVED if is_valid else ValidationStatus.REJECTED
        )
        
        return ValidationResult(
            is_valid=is_valid,
            validation_status=validation_status,
            errors=errors,
            warnings=warnings,
            checked_rules=checked_rules,
        )

    def _check_datasheet_exists(self, product_id: int) -> tuple[bool, Optional[str]]:
        """Check if product has a datasheet document."""
        datasheet = self.db.query(Document).filter(
            Document.product_id == product_id,
            Document.type == DocumentType.DATASHEET
        ).first()
        
        if not datasheet:
            return False, "No datasheet document found for this product"
        
        if not datasheet.file_url:
            return False, "Datasheet file URL is empty"
        
        return True, None

    def _check_extraction_status(
        self, product_id: int
    ) -> tuple[bool, Optional[str]]:
        """Check if datasheet extraction was successful."""
        datasheet = self.db.query(Document).filter(
            Document.product_id == product_id,
            Document.type == DocumentType.DATASHEET
        ).first()
        
        if not datasheet:
            return False, "No datasheet found"
        
        if datasheet.extraction_status == ExtractionStatus.PENDING:
            return False, "Datasheet text extraction is still pending"
        
        if datasheet.extraction_status == ExtractionStatus.FAILED:
            return False, f"Datasheet extraction failed: {datasheet.extraction_error}"
        
        if not datasheet.extracted_text:
            return False, "Datasheet extraction completed but no text was extracted"
        
        return True, None

    def _check_required_specs(
        self, product_id: int, category_name: Optional[str]
    ) -> tuple[bool, list[str], list[str]]:
        """Check if product has all required specifications for its category."""
        errors = []
        warnings = []
        
        if not category_name:
            errors.append("Product has no category assigned")
            return False, errors, warnings
        
        required_specs = REQUIRED_SPECS_BY_CATEGORY.get(category_name, [])
        
        if not required_specs:
            # No specific requirements for this category
            return True, errors, warnings
        
        # Get existing specs
        existing_specs = self.db.query(ProductSpecification).filter(
            ProductSpecification.product_id == product_id
        ).all()
        
        existing_keys = {spec.spec_key for spec in existing_specs}
        
        # Check each required spec
        for required_spec in required_specs:
            if required_spec not in existing_keys:
                errors.append(
                    f"Missing required specification for {category_name}: '{required_spec}'"
                )
        
        # Check for low confidence specs
        for spec in existing_specs:
            if spec.confidence_score < 0.5:
                warnings.append(
                    f"Specification '{spec.spec_key}' has low confidence score: {spec.confidence_score}"
                )
        
        return len(errors) == 0, errors, warnings

    def update_product_validation(
        self, product_id: int, auto_validate: bool = True
    ) -> ValidationResult:
        """
        Update product validation status after re-validation.

        Args:
            product_id: ID of the product
            auto_validate: If True, automatically set validation status

        Returns:
            ValidationResult with updated validation status
        """
        result = self.validate_product(product_id)
        
        if auto_validate:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if product:
                product.validation_status = result.validation_status
                product.is_verified = result.is_valid
                self.db.commit()
        
        return result

    def batch_validate(
        self, product_ids: list[int], auto_update: bool = True
    ) -> dict[int, ValidationResult]:
        """
        Validate multiple products in batch.

        Args:
            product_ids: List of product IDs to validate
            auto_update: If True, automatically update validation status

        Returns:
            Dictionary mapping product_id to ValidationResult
        """
        results = {}
        
        for product_id in product_ids:
            result = self.update_product_validation(product_id, auto_validate=auto_update)
            results[product_id] = result
        
        return results

    def get_validation_summary(self, results: dict[int, ValidationResult]) -> dict:
        """Get a summary of validation results."""
        total = len(results)
        valid = sum(1 for r in results.values() if r.is_valid)
        invalid = total - valid
        
        return {
            "total_products": total,
            "valid_products": valid,
            "invalid_products": invalid,
            "approval_rate": valid / total if total > 0 else 0,
            "common_errors": self._get_common_errors(results),
        }

    def _get_common_errors(self, results: dict[int, ValidationResult]) -> dict[str, int]:
        """Get count of common errors across all results."""
        error_counts = {}
        
        for result in results.values():
            for error in result.errors:
                # Normalize error for counting
                error_key = error.split(":")[0].strip()
                error_counts[error_key] = error_counts.get(error_key, 0) + 1
        
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))
