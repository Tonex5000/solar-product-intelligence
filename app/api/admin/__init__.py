"""Admin API routes package."""
from fastapi import APIRouter

from app.api.admin.companies import router as companies_router
from app.api.admin.products import router as products_router
from app.api.admin.documents import router as documents_router
from app.api.admin.categories import router as categories_router
from app.api.admin.reviews import router as reviews_router
from app.api.admin.specifications import router as specifications_router

router = APIRouter(prefix="/admin")

router.include_router(companies_router)
router.include_router(products_router)
router.include_router(documents_router)
router.include_router(categories_router)
router.include_router(reviews_router)
router.include_router(specifications_router)

__all__ = ["router"]
