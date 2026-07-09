"""Public API routes for company information."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyListResponse, CompanyResponse

router = APIRouter(prefix="/companies", tags=["Public - Companies"])


@router.get("/", response_model=CompanyListResponse)
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    verified_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all verified companies (public access).
    
    By default, only shows verified companies for data quality assurance.
    """
    query = db.query(Company)
    
    if verified_only:
        query = query.filter(Company.verified == True)
    
    total = query.count()
    companies = query.order_by(Company.name).offset(skip).limit(limit).all()
    
    return CompanyListResponse(total=total, companies=companies)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific company by ID (public access)."""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.get("/{company_id}/products", response_model=List[dict])
async def get_company_products(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all products from a company (public access)."""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    from app.models.product import Product, ValidationStatus
    
    products = db.query(Product).filter(
        Product.company_id == company_id,
        Product.validation_status == ValidationStatus.APPROVED
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "model_name": p.model_name,
            "product_name": p.product_name,
            "category": p.category.name if p.category else None,
            "is_verified": p.is_verified,
        }
        for p in products
    ]
