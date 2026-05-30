from pathlib import Path
from uuid import UUID
from uuid import uuid4

from sqlalchemy.orm import Session

from src.domain.entities.enums import DocumentStatus, DocumentType
from src.infrastructure.database.models import DocumentModel, OcrExtractionModel
from src.infrastructure.ocr.tesseract_service import TesseractOcrService
from src.shared.config.settings import settings


class DocumentUseCases:
    def __init__(self, db: Session, ocr_service: TesseractOcrService | None = None) -> None:
        self.db = db
        self.ocr_service = ocr_service or TesseractOcrService()

    def register_upload(
        self,
        file_name: str,
        content: bytes,
        shipment_id: UUID | None,
        document_type: DocumentType,
    ) -> DocumentModel:
        storage_dir = Path(settings.storage_root) / "uploads"
        storage_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{uuid4()}-{Path(file_name).name}"
        storage_path = storage_dir / safe_name
        storage_path.write_bytes(content)

        document = DocumentModel(
            shipment_id=shipment_id,
            document_type=document_type.value,
            file_name=Path(file_name).name,
            storage_path=str(storage_path),
            status=DocumentStatus.OCR_PENDING.value,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def register_generated(
        self,
        file_path: Path,
        document_type: DocumentType,
        shipment_id: UUID | None = None,
    ) -> DocumentModel:
        document = DocumentModel(
            shipment_id=shipment_id,
            document_type=document_type.value,
            file_name=file_path.name,
            storage_path=str(file_path),
            status=DocumentStatus.GENERATED.value,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def run_ocr(self, document_id: UUID) -> OcrExtractionModel:
        document = self.db.get(DocumentModel, document_id)
        if document is None:
            raise ValueError("Documento no encontrado")

        raw_text, extracted_data, confidence = self.ocr_service.extract(Path(document.storage_path))
        extraction = OcrExtractionModel(
            document_id=document.id,
            raw_text=raw_text,
            extracted_data=extracted_data,
            confidence=confidence,
        )
        document.status = DocumentStatus.OCR_PROCESSED.value
        self.db.add(extraction)
        self.db.commit()
        self.db.refresh(extraction)
        return extraction
