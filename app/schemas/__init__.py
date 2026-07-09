"""Pydantic schemas package for API request/response validation."""
from app.schemas.user import (
    LoginRequest,
    Token,
    TokenData,
    UserBase,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.schemas.company import (
    CompanyBase,
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.schemas.category import (
    CategoryBase,
    CategoryCreate,
    CategoryResponse,
)
from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentDetailResponse,
    DocumentResponse,
    DocumentUpdate,
)
from app.schemas.specification import (
    SpecificationBase,
    SpecificationCreate,
    SpecificationGroupedResponse,
    SpecificationListResponse,
    SpecificationResponse,
    SpecificationUpdate,
)
from app.schemas.company_metric import (
    CompanyMetricBase,
    CompanyMetricCreate,
    CompanyMetricResponse,
    CompanyMetricUpdate,
)
from app.schemas.review import (
    ReviewBase,
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
)

__all__ = [
    # User/Auth
    "LoginRequest",
    "Token",
    "TokenData",
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    # Company
    "CompanyBase",
    "CompanyCreate",
    "CompanyListResponse",
    "CompanyResponse",
    "CompanyUpdate",
    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryResponse",
    # Product
    "ProductBase",
    "ProductCreate",
    "ProductDetailResponse",
    "ProductListResponse",
    "ProductResponse",
    "ProductUpdate",
    # Document
    "DocumentBase",
    "DocumentCreate",
    "DocumentDetailResponse",
    "DocumentResponse",
    "DocumentUpdate",
    # Specification
    "SpecificationBase",
    "SpecificationCreate",
    "SpecificationGroupedResponse",
    "SpecificationListResponse",
    "SpecificationResponse",
    "SpecificationUpdate",
    # Company Metric
    "CompanyMetricBase",
    "CompanyMetricCreate",
    "CompanyMetricResponse",
    "CompanyMetricUpdate",
    # Review
    "ReviewBase",
    "ReviewCreate",
    "ReviewListResponse",
    "ReviewResponse",
    "ReviewUpdate",
]
