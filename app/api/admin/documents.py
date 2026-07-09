"""Admin API routes for document management."""
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.document import Document, DocumentType, ExtractionStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentDetailResponse, DocumentResponse, DocumentUpdate
from app.services.file_service import FileService
from app.services.pdf_extractor import PDFExtractor
from app.services.spec_extractor import SpecExtractor

router = APIRouter(prefix="/products/{product_id}/documents", tags=["Admin - Documents"])


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """List all documents for a product (admin only)."""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    documents = db.query(Document).filter(Document.product_id == product_id).all()
    return documents


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    product_id: int,
    document_id: int,
    include_text: bool = False,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get a specific document (admin only)."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.product_id == product_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentDetailResponse(
        id=document.id,
        product_id=document.product_id,
        type=document.type,
        file_url=document.file_url,
        extracted_text=document.extracted_text if include_text else None,
        extraction_status=document.extraction_status,
        created_at=document.created_at,
        updated_at=document.updated_at,
        extraction_error=document.extraction_error,
    )


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    product_id: int,
    document_type: DocumentType,
    file: UploadFile = File(...),
    file_url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Upload a document for a product (admin only).
    
    Either provide a file to upload OR a file_url for external storage.
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if product already has this type of document
    existing = db.query(Document).filter(
        Document.product_id == product_id,
        Document.type == document_type
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product already has a {document_type.value}. Please update or delete the existing document."
        )
    
    final_file_url = file_url
    
    # Upload file if provided
    if file and file.filename:
        file_service = FileService(db)
        file_url, error = await file_service.save_upload(file, document_type, product_id)
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File upload failed: {error}"
            )
        
        final_file_url = file_url
    
    if not final_file_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a file to upload or a file_url must be provided"
        )
    
    # Create document record
    new_document = Document(
        product_id=product_id,
        type=document_type,
        file_url=final_file_url,
        extraction_status=ExtractionStatus.PENDING,
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    # If this is a datasheet, update the product's datasheet_file_url
    if document_type == DocumentType.DATASHEET:
        product.datasheet_file_url = final_file_url
        db.commit()
    
    return new_document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    product_id: int,
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Update a document (admin only)."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.product_id == product_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    update_data = document_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    product_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Delete a document (admin only)."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.product_id == product_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from disk
    file_service = FileService(db)
    file_service.delete_file(document.file_url)
    
    db.delete(document)
    db.commit()
    
    return None


@router.post("/{document_id}/extract", response_model=dict)
async def extract_document_text(
    product_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Trigger text extraction from a document (admin only).
    
    Extracts text from PDF and stores it for future AI usage.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.product_id == product_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    extractor = PDFExtractor(db)
    success, error = extractor.process_document(document_id)
    
    # Refresh document
    db.refresh(document)
    
    return {
        "document_id": document_id,
        "success": success,
        "extraction_status": document.extraction_status.value,
        "error": error,
        "text_length": len(document.extracted_text) if document.extracted_text else 0,
    }


@router.post("/{document_id}/extract-specs", response_model=dict)
async def extract_specifications(
    product_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Extract specifications from document text (admin only).
    
    Parses extracted text to find key-value specifications.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.product_id == product_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.extraction_status != ExtractionStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text must be extracted first"
        )
    
    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extracted text available"
        )
    
    # Extract specs
    spec_extractor = SpecExtractor(db)
    specs = spec_extractor.extract_and_store(product_id, document.extracted_text)
    
    summary = spec_extractor.get_extraction_summary(
        {s.spec_key: {"value": s.spec_value, "confidence": s.confidence_score, "source": s.source_location}
         for s in specs}
    )
    
    return {
        "document_id": document_id,
        "product_id": product_id,
        "specs_extracted": len(specs),
        "specs": [{"key": s.spec_key, "value": s.spec_value, "unit": s.unit} for s in specs],
        "summary": summary,
    }
