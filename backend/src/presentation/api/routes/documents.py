import re
import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.application.dto.schemas import DocumentRead, OcrExtractionRead
from src.application.services.document_service import DocumentService
from src.domain.entities.enums import DocumentType
from src.infrastructure.repositories.document_repository import DocumentRepository
from src.infrastructure.database.session import get_db
from src.infrastructure.security.auth_handler import get_current_active_user, RoleChecker

router = APIRouter()
logger = logging.getLogger(__name__)

# Permisos por roles
allow_admin_support = RoleChecker(["ADMIN", "SALES_SUPPORT"])
allow_all_internal = RoleChecker(["ADMIN", "SALES_SUPPORT", "COMMERCIAL_AGENT"])


@router.get("", response_model=list[DocumentRead], dependencies=[Depends(allow_all_internal)])
def list_documents(db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    return repo.get_all()


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_admin_support)])
async def upload_document(
    file: UploadFile = File(...),
    shipment_id: UUID | None = Form(default=None),
    document_type: DocumentType = Form(default=DocumentType.EXTERNAL_PDF),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) :
    content = await file.read()
    original_name = Path(file.filename).name if file.filename else "documento.pdf"
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', original_name)
    
    service = DocumentService(db)
    logger.info(f"User {current_user.email} uploading document: {safe_name}")
    
    return service.register_upload(
        file_name=safe_name,
        content=content,
        shipment_id=shipment_id,
        document_type=document_type,
    )


@router.post("/{document_id}/ocr", response_model=OcrExtractionRead, dependencies=[Depends(allow_admin_support)])
def run_ocr(document_id: UUID, db: Session = Depends(get_db)):
    try:
        service = DocumentService(db)
        return service.run_ocr(document_id)
    except ValueError as exc:
        logger.error(f"OCR Failed for {document_id}: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: UUID, db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    document = repo.get_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document


@router.get("/{document_id}/download")
def download_document(document_id: UUID, db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    document = repo.get_by_id(document_id)
    
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    path = Path(document.storage_path).as_posix()
    file_path = Path(path)
    
    if not file_path.exists():
        logger.critical(f"File missing in storage: {path}")
        raise HTTPException(status_code=404, detail="Archivo no encontrado en storage")

    return FileResponse(file_path, media_type="application/pdf", filename=document.file_name)


@router.get("/{document_id}/ocr", response_model=OcrExtractionRead)
def get_ocr(document_id: UUID, db: Session = Depends(get_db)) -> OcrExtractionModel:
    extraction = db.scalar(
        select(OcrExtractionModel)
        .where(OcrExtractionModel.document_id == document_id)
        .order_by(OcrExtractionModel.created_at.desc())
    )
    if extraction is None:
        raise HTTPException(status_code=404, detail="OCR no encontrado para el documento")
    return extraction
