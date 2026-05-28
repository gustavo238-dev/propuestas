from pathlib import Path
from uuid import uuid4

from src.domain.entities.enums import DocumentType
from src.infrastructure.pdf.reportlab_service import ReportLabPdfService
from src.shared.config.settings import settings


class PdfDocumentUseCases:
    def __init__(self, pdf_service: ReportLabPdfService | None = None) -> None:
        self.pdf_service = pdf_service or ReportLabPdfService()

    def generate(self, document_type: DocumentType, payload: dict) -> Path:
        output_dir = Path(settings.storage_root) / "generated"
        file_name = f"{document_type.value.lower()}-{uuid4()}.pdf"
        return self.pdf_service.generate_business_pdf(
            title=self._title_for(document_type),
            payload=payload,
            output_path=output_dir / file_name,
        )

    @staticmethod
    def _title_for(document_type: DocumentType) -> str:
        titles = {
            DocumentType.INVOICE: "Factura",
            DocumentType.QUOTATION: "Cotizacion",
            DocumentType.LOGISTICS_GUIDE: "Guia Logistica",
            DocumentType.REPORT: "Reporte",
            DocumentType.DRAFT: "Draft",
            DocumentType.RECEIPT: "Comprobante",
            DocumentType.SHIPMENT_SUMMARY: "Resumen de Embarque",
        }
        return titles.get(document_type, "Documento")
