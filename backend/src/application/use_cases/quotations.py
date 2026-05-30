from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from src.application.dto.schemas import QuotationCreate
from src.domain.entities.enums import QuotationStatus
from src.infrastructure.database.models import QuotationModel


class QuotationUseCases:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: QuotationCreate, requested_by_id: UUID | None = None) -> QuotationModel:
        quotation = QuotationModel(**payload.model_dump(), requested_by_id=requested_by_id)
        self.db.add(quotation)
        self.db.commit()
        self.db.refresh(quotation)
        return quotation

    def approve(self, quotation_id: UUID) -> QuotationModel:
        quotation = self.db.get(QuotationModel, quotation_id)
        if quotation is None:
            raise ValueError("Cotizacion no encontrada")
        quotation.status = QuotationStatus.APPROVED.value
        quotation.decided_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(quotation)
        return quotation

    def reject(self, quotation_id: UUID) -> QuotationModel:
        quotation = self.db.get(QuotationModel, quotation_id)
        if quotation is None:
            raise ValueError("Cotizacion no encontrada")
        quotation.status = QuotationStatus.REJECTED.value
        quotation.decided_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(quotation)
        return quotation
