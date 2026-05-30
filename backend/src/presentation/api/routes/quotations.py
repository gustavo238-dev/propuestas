from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import QuotationCreate, QuotationRead
from src.application.use_cases.quotations import QuotationUseCases
from src.infrastructure.database.models import QuotationModel
from src.infrastructure.database.session import get_db

router = APIRouter()


@router.get("", response_model=list[QuotationRead])
def list_quotations(db: Session = Depends(get_db)) -> list[QuotationModel]:
    return list(db.scalars(select(QuotationModel).order_by(QuotationModel.created_at.desc())))


@router.post("", response_model=QuotationRead, status_code=status.HTTP_201_CREATED)
def create_quotation(payload: QuotationCreate, db: Session = Depends(get_db)) -> QuotationModel:
    return QuotationUseCases(db).create(payload)


@router.get("/{quotation_id}", response_model=QuotationRead)
def get_quotation(quotation_id: UUID, db: Session = Depends(get_db)) -> QuotationModel:
    quotation = db.get(QuotationModel, quotation_id)
    if quotation is None:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")
    return quotation


@router.post("/{quotation_id}/approve", response_model=QuotationRead)
def approve_quotation(quotation_id: UUID, db: Session = Depends(get_db)) -> QuotationModel:
    try:
        return QuotationUseCases(db).approve(quotation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{quotation_id}/reject", response_model=QuotationRead)
def reject_quotation(quotation_id: UUID, db: Session = Depends(get_db)) -> QuotationModel:
    try:
        return QuotationUseCases(db).reject(quotation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
