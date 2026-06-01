from uuid import UUID

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import DocumentRead, OcrExtractionRead
from src.application.use_cases.documents import DocumentUseCases
from src.domain.entities.enums import DocumentType
from src.infrastructure.database.models import DocumentModel, OcrExtractionModel
from src.infrastructure.database.session import get_db

router = APIRouter()


@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentModel]:
    return list(db.scalars(select(DocumentModel).order_by(DocumentModel.created_at.desc())))


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    shipment_id: UUID | None = Form(default=None),
    document_type: DocumentType = Form(default=DocumentType.EXTERNAL_PDF),
    db: Session = Depends(get_db),
) -> DocumentModel:
    content = await file.read()
    return DocumentUseCases(db).register_upload(
        file_name=file.filename or "documento.pdf",
        content=content,
        shipment_id=shipment_id,
        document_type=document_type,
    )


@router.post("/{document_id}/ocr", response_model=OcrExtractionRead)
def run_ocr(document_id: UUID, db: Session = Depends(get_db)) -> OcrExtractionRead:
    try:
        return DocumentUseCases(db).run_ocr(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: UUID, db: Session = Depends(get_db)) -> DocumentModel:
    document = db.get(DocumentModel, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document


@router.get("/{document_id}/download")
def download_document(document_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    document = db.get(DocumentModel, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    path = Path(document.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado en storage")

    response = FileResponse(path, media_type="application/pdf")
    # Prefer inline disposition so browsers can render the PDF inside iframes
    response.headers["Content-Disposition"] = f'inline; filename="{document.file_name}"'
    return response


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
