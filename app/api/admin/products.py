"""Admin API routes for product management."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.product import Product, ValidationStatus
from app.models.user import User
from app.schemas.product import ProductCreate, ProductDetailResponse, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Admin - Products"])


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    category_id: Optional[int] = None,
    validation_status: Optional[ValidationStatus] = None,
    verified_only: bool = False,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """List all products (admin only)."""
    query = db.query(Product)
    
    if company_id:
        query = query.filter(Product.company_id == company_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if validation_status:
        query = query.filter(Product.validation_status == validation_status)
    if verified_only:
        query = query.filter(Product.is_verified == True)
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get a specific product by ID (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    response = ProductDetailResponse(
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
    
    return response


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new product (admin only).
    
    STRICT RULE: Product MUST have a datasheet_file_url. Without it, the product will be rejected.
    """
    # Validate datasheet is provided (enforced by schema, but double-check)
    if not product_data.datasheet_file_url or product_data.datasheet_file_url.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product MUST have an official datasheet URL. This is a strict requirement."
        )
    
    # Verify company exists
    from app.models.company import Company
    company = db.query(Company).filter(Company.id == product_data.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with ID {product_data.company_id} not found"
        )
    
    # Verify category exists
    from app.models.category import Category
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with ID {product_data.category_id} not found"
        )
    
    # Create product with pending validation status
    new_product = Product(
        **product_data.model_dump(),
        validation_status=ValidationStatus.PENDING,
        is_verified=False,
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Update a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Validate datasheet if being updated
    if product_data.datasheet_file_url is not None and product_data.datasheet_file_url.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product MUST have an official datasheet URL"
        )
    
    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Delete a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    
    return None


@router.post("/{product_id}/validate", response_model=dict)
async def validate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Trigger product validation (admin only)."""
    from app.services.validation_engine import ValidationEngine
    
    engine = ValidationEngine(db)
    result = engine.update_product_validation(product_id)
    
    return {
        "product_id": product_id,
        "is_valid": result.is_valid,
        "validation_status": result.validation_status.value,
        "errors": result.errors,
        "warnings": result.warnings,
        "checked_rules": result.checked_rules,
    }


@router.post("/{product_id}/approve", response_model=ProductResponse)
async def approve_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Manually approve a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.validation_status = ValidationStatus.APPROVED
    product.is_verified = True
    db.commit()
    db.refresh(product)
    
    return product


@router.post("/{product_id}/reject", response_model=ProductResponse)
async def reject_product(
    product_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Manually reject a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.validation_status = ValidationStatus.REJECTED
    product.is_verified = False
    db.commit()
    db.refresh(product)
    
    return product
