"""Tests for category endpoints."""
import pytest


class TestCategories:
    """Test category endpoints."""

    def test_list_categories_admin(self, client, admin_headers, test_categories):
        """Test listing categories as admin."""
        response = client.get("/api/admin/categories", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # Default categories
        category_names = [c["name"] for c in data]
        assert "battery" in category_names
        assert "inverter" in category_names
        assert "solar_panel" in category_names
        assert "charge_controller" in category_names

    def test_list_categories_public(self, client, test_categories):
        """Test listing categories publicly."""
        response = client.get("/api/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_get_category_by_id(self, client, admin_headers, test_categories):
        """Test getting a specific category by ID."""
        response = client.get("/api/admin/categories/1", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data

    def test_create_category(self, client, admin_headers):
        """Test creating a new category."""
        response = client.post(
            "/api/admin/categories",
            headers=admin_headers,
            json={
                "name": "monitoring",
                "description": "Solar monitoring systems"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "monitoring"
        assert data["description"] == "Solar monitoring systems"

    def test_create_duplicate_category(self, client, admin_headers, test_categories):
        """Test creating a duplicate category."""
        response = client.post(
            "/api/admin/categories",
            headers=admin_headers,
            json={"name": "battery"}
        )
        
        assert response.status_code == 400

    def test_delete_category(self, client, admin_headers):
        """Test deleting a category."""
        # First create a category
        create_response = client.post(
            "/api/admin/categories",
            headers=admin_headers,
            json={"name": "temporary", "description": "Temp category"}
        )
        category_id = create_response.json()["id"]
        
        # Then delete it
        response = client.delete(
            f"/api/admin/categories/{category_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 204
