"""Tests for product endpoints."""
import pytest


class TestProducts:
    """Test product endpoints."""

    @pytest.fixture
    def test_company(self, client, admin_headers):
        """Create a test company."""
        response = client.post(
            "/api/admin/companies",
            headers=admin_headers,
            json={"name": "Test Solar Co", "country": "Germany"}
        )
        return response.json()

    @pytest.fixture
    def test_category(self, client, admin_headers, test_categories):
        """Get a test category."""
        return test_categories[0]  # battery

    def test_create_product_requires_datasheet(self, client, admin_headers, test_company, test_category):
        """Test that creating a product requires a datasheet URL."""
        response = client.post(
            "/api/admin/products",
            headers=admin_headers,
            json={
                "company_id": test_company["id"],
                "category_id": test_category.id,
                "model_name": "TEST-001",
                "product_name": "Test Battery",
                "description": "A test battery product",
                # No datasheet_file_url - should fail
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_product_with_datasheet(self, client, admin_headers, test_company, test_category):
        """Test creating a product with datasheet URL."""
        response = client.post(
            "/api/admin/products",
            headers=admin_headers,
            json={
                "company_id": test_company["id"],
                "category_id": test_category.id,
                "model_name": "TEST-001",
                "product_name": "Test Battery",
                "description": "A test battery product",
                "datasheet_file_url": "https://example.com/datasheets/test-001.pdf",
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["model_name"] == "TEST-001"
        assert data["validation_status"] == "pending"
        assert data["is_verified"] is False

    def test_list_products_admin(self, client, admin_headers, test_company, test_category):
        """Test listing products as admin."""
        # Create a product
        client.post(
            "/api/admin/products",
            headers=admin_headers,
            json={
                "company_id": test_company["id"],
                "category_id": test_category.id,
                "model_name": "ADMIN-TEST-001",
                "product_name": "Admin Test Battery",
                "datasheet_file_url": "https://example.com/datasheet.pdf",
            }
        )
        
        response = client.get("/api/admin/products", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_list_products_public_only_approved(self, client, admin_headers, test_company, test_category):
        """Test that public users only see approved products."""
        # Create a pending product
        client.post(
            "/api/admin/products",
            headers=admin_headers,
            json={
                "company_id": test_company["id"],
                "category_id": test_category.id,
                "model_name": "PENDING-001",
                "product_name": "Pending Product",
                "datasheet_file_url": "https://example.com/pending.pdf",
            }
        )
        
        # Public listing should be empty
        response = client.get("/api/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_approve_product(self, client, admin_headers, test_company, test_category):
        """Test approving a product."""
        # Create product
        create_response = client.post(
            "/api/admin/products",
            headers=admin_headers,
            json={
                "company_id": test_company["id"],
                "category_id": test_category.id,
                "model_name": "TO-APPROVE-001",
                "product_name": "Product to Approve",
                "datasheet_file_url": "https://example.com/toapprove.pdf",
            }
        )
        product_id = create_response.json()["id"]
        
        # Approve it
        response = client.post(
            f"/api/admin/products/{product_id}/approve",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["validation_status"] == "approved"
        assert data["is_verified"] is True
        
        # Now public can see it
        public_response = client.get("/api/products")
        assert public_response.json()["total"] == 1

    def test_validate_product(self, client, admin_headers, test_company, test_category):
        """Test product validation engine."""
        # Create product
        create_response = client.post(
            "/api/admin/products",
            headers=admin_headers,
            json={
                "company_id": test_company["id"],
                "category_id": test_category.id,
                "model_name": "VALIDATE-001",
                "product_name": "Product to Validate",
                "datasheet_file_url": "https://example.com/validate.pdf",
            }
        )
        product_id = create_response.json()["id"]
        
        # Validate it
        response = client.post(
            f"/api/admin/products/{product_id}/validate",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should be rejected because it has no datasheet document uploaded
        assert data["validation_status"] == "rejected"
        assert len(data["errors"]) > 0
