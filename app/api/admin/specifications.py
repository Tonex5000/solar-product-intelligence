"""Admin API routes for specification management."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.product import Product
from app.models.specification import ProductSpecification
from app.models.user import User
from app.schemas.specification import (
    SpecificationCreate,
    SpecificationGroupedResponse,
    SpecificationResponse,
    SpecificationUpdate,
)

router = APIRouter(prefix="/products/{product_id}/specifications", tags=["Admin - Specifications"])


@router.get("/", response_model=List[SpecificationResponse])
async def list_specifications(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """List all specifications for a product (admin only)."""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    specs = db.query(ProductSpecification).filter(
        ProductSpecification.product_id == product_id
    ).all()
    
    return specs


@router.get("/grouped", response_model=SpecificationGroupedResponse)
async def get_grouped_specifications(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get specifications grouped by key prefix (admin only)."""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    specs = db.query(ProductSpecification).filter(
        ProductSpecification.product_id == product_id
    ).all()
    
    # Group by prefix (e.g., 'voltage', 'max_current', etc.)
    groups = {}
    for spec in specs:
        # Extract group from spec_key (everything before the last underscore or the whole key)
        parts = spec.spec_key.rsplit('_', 1)
        if len(parts) > 1 and parts[0] in ['max', 'min', 'rated', 'nominal']:
            group = parts[0]
        else:
            group = spec.spec_key
        
        if group not in groups:
            groups[group] = []
        groups[group].append(SpecificationResponse.model_validate(spec))
    
    return SpecificationGroupedResponse(groups=groups)


@router.post("/", response_model=SpecificationResponse, status_code=status.HTTP_201_CREATED)
async def create_specification(
    product_id: int,
    spec_data: SpecificationCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Create a new specification manually (admin only)."""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Override product_id from path
    spec_data.product_id = product_id
    
    new_spec = ProductSpecification(**spec_data.model_dump())
    
    db.add(new_spec)
    db.commit()
    db.refresh(new_spec)
    
    return new_spec


@router.put("/{spec_id}", response_model=SpecificationResponse)
async def update_specification(
    product_id: int,
    spec_id: int,
    spec_data: SpecificationUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Update a specification (admin only)."""
    spec = db.query(ProductSpecification).filter(
        ProductSpecification.id == spec_id,
        ProductSpecification.product_id == product_id
    ).first()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    update_data = spec_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(spec, field, value)
    
    db.commit()
    db.refresh(spec)
    
    return spec


@router.delete("/{spec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specification(
    product_id: int,
    spec_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Delete a specification (admin only)."""
    spec = db.query(ProductSpecification).filter(
        ProductSpecification.id == spec_id,
        ProductSpecification.product_id == product_id
    ).first()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification not found"
        )
    
    db.delete(spec)
    db.commit()
    
    return None


@router.delete("/by-key/{spec_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specifications_by_key(
    product_id: int,
    spec_key: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Delete all specifications with a given key for a product (admin only)."""
    specs = db.query(ProductSpecification).filter(
        ProductSpecification.product_id == product_id,
        ProductSpecification.spec_key == spec_key
    ).all()
    
    for spec in specs:
        db.delete(spec)
    
    db.commit()
    
    return None
