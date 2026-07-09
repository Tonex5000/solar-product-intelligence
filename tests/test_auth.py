"""Tests for authentication endpoints."""
import pytest


class TestAuth:
    """Test authentication endpoints."""

    def test_login_success(self, client, admin_user):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpassword"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, admin_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        
        assert response.status_code == 401

    def test_register_new_user(self, client):
        """Test registering a new user."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["is_admin"] is True

    def test_register_duplicate_username(self, client, admin_user):
        """Test registering with duplicate username."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testadmin",
                "email": "different@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400

    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/admin/companies")
        
        assert response.status_code == 401

    def test_protected_endpoint_with_token(self, client, admin_headers, test_categories):
        """Test accessing protected endpoint with valid token."""
        response = client.get("/api/admin/categories", headers=admin_headers)
        
        assert response.status_code == 200
