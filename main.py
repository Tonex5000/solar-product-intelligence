"""
Solar Product Intelligence Backend System

A FastAPI-based backend for managing solar products with strict data integrity rules.
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import engine, Base
from app.api import admin as admin_api
from app.api import public as public_api
from app.api.auth import router as auth_router
from app.api.simulation import router as simulation_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Solar Product Intelligence Backend...")
    logger.info(f"Application: {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    # Create database tables if they don't exist
    init_db()
    
    # Run seed in development only
    if settings.DEBUG or os.environ.get("RUN_SEED", "").lower() == "true":
        from app.db.seed import seed_all
        try:
            seed_all()
        except Exception as e:
            logger.warning(f"Seed already exists or failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Solar Product Intelligence Backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Solar Product Intelligence Backend System

A production-ready backend for managing solar products with strict data integrity rules.

### Features
- **Strict Data Validation**: Every product requires an official datasheet
- **Admin-Controlled Ingestion**: Only admins can add products and data
- **PDF Text Extraction**: Extract text from datasheets for AI usage
- **Automated Spec Extraction**: Parse technical specifications from documents
- **Product Validation Engine**: Enforce quality standards automatically
- **Solar Simulation Engine**: Realistic solar system behavior simulation

### Authentication
- Admin endpoints require JWT authentication
- Public endpoints are accessible without authentication

### Data Integrity Rules
1. No external datasets - all data is admin-controlled
2. No public/user uploads - only admin ingestion
3. Every product MUST have an official datasheet
4. No datasheet = reject product
5. All specs must be extracted from datasheet text
6. System stores both structured specs and raw document text
    """,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
# Authentication routes
app.include_router(auth_router, prefix="/api")

# Admin routes
app.include_router(admin_api.router, prefix="/api")

# Public routes
app.include_router(public_api.router, prefix="/api")

# Simulation routes
app.include_router(simulation_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "database": "connected",
    }


@app.get("/api/info", tags=["Information"])
async def api_info():
    """Get API information and available endpoints."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "auth": {
                "login": "POST /api/auth/login",
                "register": "POST /api/auth/register",
            },
            "admin": {
                "companies": "/api/admin/companies",
                "products": "/api/admin/products",
                "categories": "/api/admin/categories",
                "documents": "/api/admin/products/{id}/documents",
                "specifications": "/api/admin/products/{id}/specifications",
                "reviews": "/api/admin/reviews",
            },
            "public": {
                "companies": "/api/companies",
                "products": "/api/products",
                "categories": "/api/categories",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
