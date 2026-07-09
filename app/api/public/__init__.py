"""Public API routes package."""
from fastapi import APIRouter

from app.api.public.companies import router as companies_router
from app.api.public.products import router as products_router
from app.api.public.categories import router as categories_router

router = APIRouter()

router.include_router(companies_router)
router.include_router(products_router)
router.include_router(categories_router)

__all__ = ["router"]
