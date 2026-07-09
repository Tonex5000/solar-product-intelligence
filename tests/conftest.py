"""Test configuration and fixtures."""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.core.database import Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.category import Category, DEFAULT_CATEGORIES


# Create test database
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Create a test database session."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client."""
    from fastapi.testclient import TestClient
    from app.core.database import get_db
    
    # Import app after setting test environment
    from main import app
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db):
    """Create a test admin user."""
    user = User(
        username="testadmin",
        email="testadmin@example.com",
        full_name="Test Admin",
        hashed_password=get_password_hash("testpassword"),
        is_admin=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """Get an admin authentication token."""
    response = client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "testpassword"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    """Get admin authorization headers."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def test_categories(db):
    """Create test categories."""
    categories = []
    for cat_data in DEFAULT_CATEGORIES:
        category = Category(**cat_data)
        db.add(category)
        categories.append(category)
    db.commit()
    for cat in categories:
        db.refresh(cat)
    return categories
