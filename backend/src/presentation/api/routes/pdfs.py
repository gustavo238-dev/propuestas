from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.application.dto.schemas import PdfGeneratedRead
from src.application.use_cases.documents import DocumentUseCases
from src.application.use_cases.pdf_documents import PdfDocumentUseCases
from src.domain.entities.enums import DocumentType
from src.infrastructure.database.session import get_db

router = APIRouter()


@router.post("/invoices")
def generate_invoice(payload: dict) -> FileResponse:
    return _generate_file(DocumentType.INVOICE, payload)


@router.post("/invoices/store", response_model=PdfGeneratedRead)
def generate_and_store_invoice(
    payload: dict,
    shipment_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> PdfGeneratedRead:
    path = PdfDocumentUseCases().generate(DocumentType.INVOICE, payload)
    document = DocumentUseCases(db).register_generated(path, DocumentType.INVOICE, shipment_id)
    return PdfGeneratedRead(
        document=document,
        download_url=f"/api/v1/documents/{document.id}/download",
    )


@router.post("/quotations")
def generate_quotation_pdf(payload: dict) -> FileResponse:
    return _generate_file(DocumentType.QUOTATION, payload)


@router.post("/logistics-guides")
def generate_logistics_guide(payload: dict) -> FileResponse:
    return _generate_file(DocumentType.LOGISTICS_GUIDE, payload)


@router.post("/reports")
def generate_report(payload: dict) -> FileResponse:
    return _generate_file(DocumentType.REPORT, payload)


@router.post("/drafts")
def generate_draft(payload: dict) -> FileResponse:
    return _generate_file(DocumentType.DRAFT, payload)


@router.post("/receipts")
def generate_receipt(payload: dict) -> FileResponse:
    return _generate_file(DocumentType.RECEIPT, payload)


@router.post("/shipment-summaries")
def generate_shipment_summary(payload: dict) -> FileResponse:
    return _generate_file(DocumentType.SHIPMENT_SUMMARY, payload)


def _generate_file(document_type: DocumentType, payload: dict) -> FileResponse:
    path: Path = PdfDocumentUseCases().generate(document_type, payload)
    return FileResponse(path, media_type="application/pdf", filename=path.name)
