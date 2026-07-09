"""Public API routes for category information."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Public - Categories"])


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    db: Session = Depends(get_db)
):
    """List all product categories (public access)."""
    categories = db.query(Category).order_by(Category.name).all()
    return categories


@router.get("/{category_name}/products", response_model=dict)
async def get_category_products(
    category_name: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all approved products in a category (public access)."""
    from app.models.product import Product, ValidationStatus
    
    category = db.query(Category).filter(Category.name == category_name).first()
    
    if not category:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    products = db.query(Product).filter(
        Product.category_id == category.id,
        Product.validation_status == ValidationStatus.APPROVED
    ).offset(skip).limit(limit).all()
    
    total = db.query(Product).filter(
        Product.category_id == category.id,
        Product.validation_status == ValidationStatus.APPROVED
    ).count()
    
    return {
        "category": category.name,
        "category_description": category.description,
        "total": total,
        "products": [
            {
                "id": p.id,
                "model_name": p.model_name,
                "product_name": p.product_name,
                "company_name": p.company.name if p.company else None,
            }
            for p in products
        ],
    }
