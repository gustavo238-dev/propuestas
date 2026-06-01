import logging
import re
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import DocumentRead, OcrExtractionRead
from src.application.use_cases.documents import DocumentUseCases
from src.domain.entities.enums import DocumentStatus, DocumentType
from src.infrastructure.database.models import DocumentModel, OcrExtractionModel
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.document_repository import DocumentRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentModel]:
    return DocumentRepository(db).get_all()


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    shipment_id: UUID | None = Form(default=None),
    document_type: DocumentType = Form(default=DocumentType.EXTERNAL_PDF),
    db: Session = Depends(get_db),
) -> DocumentModel:
    content = await file.read()
    original_name = Path(file.filename).name if file.filename else "documento.pdf"
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", original_name)

    logger.info("Uploading document: %s", safe_name)
    return DocumentUseCases(db).register_upload(
        file_name=safe_name,
        content=content,
        shipment_id=shipment_id,
        document_type=document_type,
    )


@router.post("/{document_id}/ocr", response_model=OcrExtractionRead)
def run_ocr(document_id: UUID, db: Session = Depends(get_db)) -> OcrExtractionModel:
    try:
        return DocumentUseCases(db).run_ocr(document_id)
    except ValueError as exc:
        logger.error("OCR failed for %s: %s", document_id, str(exc))
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: UUID, db: Session = Depends(get_db)) -> DocumentModel:
    document = DocumentRepository(db).get_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document


@router.get("/{document_id}/download")
def download_document(document_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    document = DocumentRepository(db).get_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    file_path = Path(Path(document.storage_path).as_posix())
    if not file_path.exists():
        logger.critical("File missing in storage: %s", file_path)
        raise HTTPException(status_code=404, detail="Archivo no encontrado en storage")

    return FileResponse(file_path, media_type="application/pdf", filename=document.file_name)


@router.get("/{document_id}/ocr", response_model=OcrExtractionRead)
def get_ocr(document_id: UUID, db: Session = Depends(get_db)) -> OcrExtractionModel:
    extraction = _latest_extraction(db, document_id)
    if extraction is None:
        raise HTTPException(status_code=404, detail="OCR no encontrado para el documento")
    return extraction


@router.post("/{document_id}/ocr/validate", response_model=OcrExtractionRead)
def validate_ocr(document_id: UUID, db: Session = Depends(get_db)) -> OcrExtractionModel:
    document = db.get(DocumentModel, document_id)
    extraction = _latest_extraction(db, document_id)
    if document is None or extraction is None:
        raise HTTPException(status_code=404, detail="OCR no encontrado para validar")

    extraction.validation_status = "VALIDATED"
    document.status = DocumentStatus.VALIDATED.value
    db.commit()
    db.refresh(extraction)
    return extraction


def _latest_extraction(db: Session, document_id: UUID) -> OcrExtractionModel | None:
    return db.scalar(
        select(OcrExtractionModel)
        .where(OcrExtractionModel.document_id == document_id)
        .order_by(OcrExtractionModel.created_at.desc())
    )
