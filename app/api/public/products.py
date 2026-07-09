"""Public API routes for product information."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product, ValidationStatus
from app.schemas.product import ProductDetailResponse, ProductListResponse, ProductResponse

router = APIRouter(prefix="/products", tags=["Public - Products"])


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = 0,
    limit: int = 20,
    company_id: Optional[int] = None,
    category_id: Optional[int] = None,
    category_name: Optional[str] = None,
    verified_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all approved products (public access).
    
    Only shows verified/approved products for data quality assurance.
    """
    query = db.query(Product)
    
    # Only show approved products to public
    if verified_only:
        query = query.filter(Product.validation_status == ValidationStatus.APPROVED)
    
    if company_id:
        query = query.filter(Product.company_id == company_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if category_name:
        from app.models.category import Category
        category = db.query(Category).filter(Category.name == category_name).first()
        if category:
            query = query.filter(Product.category_id == category.id)
    
    total = query.count()
    products = query.order_by(Product.product_name).offset(skip).limit(limit).all()
    
    return ProductListResponse(total=total, products=products)


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed product information (public access).
    
    Returns product details including company and category information.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Only show approved products to public
    if product.validation_status != ValidationStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductDetailResponse(
        id=product.id,
        company_id=product.company_id,
        category_id=product.category_id,
        model_name=product.model_name,
        product_name=product.product_name,
        description=product.description,
        datasheet_file_url=product.datasheet_file_url,
        manual_file_url=product.manual_file_url,
        validation_status=product.validation_status,
        is_verified=product.is_verified,
        created_at=product.created_at,
        updated_at=product.updated_at,
        company_name=product.company.name if product.company else None,
        category_name=product.category.name if product.category else None,
    )


@router.get("/{product_id}/specs", response_model=dict)
async def get_product_specifications(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get all specifications for a product (public access)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Only show approved products to public
    if product.validation_status != ValidationStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    from app.models.specification import ProductSpecification
    specs = db.query(ProductSpecification).filter(
        ProductSpecification.product_id == product_id
    ).all()
    
    return {
        "product_id": product_id,
        "model_name": product.model_name,
        "specifications": [
            {
                "key": s.spec_key,
                "value": s.spec_value,
                "unit": s.unit,
            }
            for s in specs
        ],
    }


@router.get("/{product_id}/documents", response_model=dict)
async def get_product_documents(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get document URLs for a product (public access)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Only show approved products to public
    if product.validation_status != ValidationStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {
        "product_id": product_id,
        "model_name": product.model_name,
        "datasheet_url": product.datasheet_file_url,
        "manual_url": product.manual_file_url,
    }


@router.get("/search/", response_model=ProductListResponse)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search products by name or model (public access)."""
    query = db.query(Product).filter(
        Product.validation_status == ValidationStatus.APPROVED
    )
    
    search_filter = (
        Product.product_name.ilike(f"%{q}%") |
        Product.model_name.ilike(f"%{q}%") |
        Product.description.ilike(f"%{q}%")
    )
    
    query = query.filter(search_filter)
    
    total = query.count()
    products = query.order_by(Product.product_name).offset(skip).limit(limit).all()
    
    return ProductListResponse(total=total, products=products)
