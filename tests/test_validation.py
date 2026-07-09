"""Tests for validation engine."""
import pytest
from app.models.product import ValidationStatus
from app.models.document import DocumentType, ExtractionStatus
from app.models.specification import ProductSpecification
from app.services.validation_engine import ValidationEngine


class TestValidationEngine:
    """Test product validation engine."""

    @pytest.fixture
    def test_company_fixture(self, client, admin_headers):
        """Create a test company using API."""
        response = client.post(
            "/api/admin/companies",
            headers=admin_headers,
            json={"name": "Test Company", "country": "USA"}
        )
        return response.json()

    @pytest.fixture
    def test_category_fixture(self, test_categories):
        """Get a test category."""
        return test_categories[0]  # battery

    @pytest.fixture
    def product_with_datasheet(self, db, test_company_fixture, test_category_fixture):
        """Create a product with datasheet document."""
        from app.models.product import Product
        from app.models.document import Document
        
        # Create product
        product = Product(
            company_id=test_company_fixture["id"],
            category_id=test_category_fixture.id,
            model_name="TEST-001",
            product_name="Test Product",
            datasheet_file_url="https://example.com/datasheet.pdf",
            validation_status=ValidationStatus.PENDING,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Create datasheet document
        document = Document(
            product_id=product.id,
            type=DocumentType.DATASHEET,
            file_url="https://example.com/datasheet.pdf",
            extracted_text="Voltage: 48V, Capacity: 100Ah, Cycle Life: 6000 cycles",
            extraction_status=ExtractionStatus.SUCCESS,
        )
        db.add(document)
        db.commit()
        
        return product

    def test_validation_requires_datasheet_document(self, db, test_company_fixture, test_category_fixture):
        """Test that validation requires a datasheet document."""
        from app.models.product import Product
        
        # Create product without datasheet document
        product = Product(
            company_id=test_company_fixture["id"],
            category_id=test_category_fixture.id,
            model_name="NO-DOC-001",
            product_name="Product Without Document",
            datasheet_file_url="https://example.com/datasheet.pdf",
            validation_status=ValidationStatus.PENDING,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        engine = ValidationEngine(db)
        result = engine.validate_product(product.id)
        
        assert result.is_valid is False
        assert any("Datasheet" in error for error in result.errors)

    def test_validation_requires_successful_extraction(
        self, db, test_company_fixture, test_category_fixture
    ):
        """Test that validation requires successful text extraction."""
        from app.models.product import Product
        from app.models.document import Document
        
        # Create product with pending extraction
        product = Product(
            company_id=test_company_fixture["id"],
            category_id=test_category_fixture.id,
            model_name="PENDING-EXT-001",
            product_name="Product with Pending Extraction",
            datasheet_file_url="https://example.com/datasheet.pdf",
            validation_status=ValidationStatus.PENDING,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Create document with pending extraction
        document = Document(
            product_id=product.id,
            type=DocumentType.DATASHEET,
            file_url="https://example.com/datasheet.pdf",
            extraction_status=ExtractionStatus.PENDING,
        )
        db.add(document)
        db.commit()
        
        engine = ValidationEngine(db)
        result = engine.validate_product(product.id)
        
        assert result.is_valid is False
        assert any("Extraction" in error or "pending" in error.lower() for error in result.errors)

    def test_validation_checks_required_specs(self, db, product_with_datasheet):
        """Test that validation checks for required specifications."""
        engine = ValidationEngine(db)
        result = engine.validate_product(product_with_datasheet.id)
        
        # Should be valid since the sample text contains the required specs
        # This depends on the actual spec extraction logic
        # For a battery category, required specs are: voltage, capacity, cycle_life
        assert result.checked_rules["has_datasheet"] is True
        assert result.checked_rules["extraction_successful"] is True

    def test_validation_updates_product_status(self, db, product_with_datasheet):
        """Test that validation updates product status."""
        # Add required specs
        specs = [
            ("voltage", "48", "V"),
            ("capacity", "100", "Ah"),
            ("cycle_life", "6000", "cycles"),
        ]
        for key, value, unit in specs:
            spec = ProductSpecification(
                product_id=product_with_datasheet.id,
                spec_key=key,
                spec_value=value,
                unit=unit,
                confidence_score=1.0,
            )
            db.add(spec)
        db.commit()
        
        engine = ValidationEngine(db)
        result = engine.update_product_validation(product_with_datasheet.id)
        
        assert result.is_valid is True
        assert result.validation_status == ValidationStatus.APPROVED
        
        # Refresh and check product
        db.refresh(product_with_datasheet)
        assert product_with_datasheet.validation_status == ValidationStatus.APPROVED
        assert product_with_datasheet.is_verified is True
