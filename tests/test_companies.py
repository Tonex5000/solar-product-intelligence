"""Tests for company endpoints."""
import pytest


class TestCompanies:
    """Test company endpoints."""

    def test_create_company(self, client, admin_headers):
        """Test creating a new company."""
        response = client.post(
            "/api/admin/companies",
            headers=admin_headers,
            json={
                "name": "SolarTech Inc",
                "country": "USA",
                "website": "https://solartech.example.com",
                "support_email": "support@solartech.example.com",
                "support_phone": "+1-800-555-0123",
                "warranty_info": "10 year limited warranty"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "SolarTech Inc"
        assert data["country"] == "USA"
        assert data["verified"] is False

    def test_list_companies(self, client, admin_headers):
        """Test listing companies as admin."""
        # Create a company first
        client.post(
            "/api/admin/companies",
            headers=admin_headers,
            json={"name": "Test Company", "country": "Germany"}
        )
        
        response = client.get("/api/admin/companies", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_list_verified_companies_public(self, client, admin_headers):
        """Test listing only verified companies publicly."""
        # Create and verify a company
        create_response = client.post(
            "/api/admin/companies",
            headers=admin_headers,
            json={"name": "Verified Corp", "country": "Japan"}
        )
        company_id = create_response.json()["id"]
        
        # Verify the company
        client.post(
            f"/api/admin/companies/{company_id}/verify",
            headers=admin_headers
        )
        
        # Create unverified company
        client.post(
            "/api/admin/companies",
            headers=admin_headers,
            json={"name": "Unverified Corp", "country": "France"}
        )
        
        # Public listing should only show verified
        response = client.get("/api/companies?verified_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["companies"][0]["name"] == "Verified Corp"

    def test_verify_company(self, client, admin_headers):
        """Test verifying a company."""
        # Create company
        create_response = client.post(
            "/api/admin/companies",
            headers=admin_headers,
            json={"name": "To Verify Corp", "country": "Canada"}
        )
        company_id = create_response.json()["id"]
        
        # Verify it
        response = client.post(
            f"/api/admin/companies/{company_id}/verify",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert response.json()["verified"] is True

    def test_update_company(self, client, admin_headers):
        """Test updating a company."""
        # Create company
        create_response = client.post(
            "/api/admin/companies",
            headers=admin_headers,
            json={"name": "Original Name", "country": "Brazil"}
        )
        company_id = create_response.json()["id"]
        
        # Update it
        response = client.put(
            f"/api/admin/companies/{company_id}",
            headers=admin_headers,
            json={"name": "Updated Name", "country": "Brazil", "website": "https://newsite.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["website"] == "https://newsite.com"
