from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.application.dto.schemas import CompanyCreate, CompanyRead, ContactCreate, ContactRead
from src.infrastructure.database.models import CompanyModel, ContactModel
from src.infrastructure.database.session import get_db

router = APIRouter()


@router.get("", response_model=list[CompanyRead])
def list_companies(tax_id: str | None = None, db: Session = Depends(get_db)) -> list[CompanyModel]:
    statement = select(CompanyModel)
    if tax_id:
        statement = statement.where(CompanyModel.tax_id == tax_id)
    return list(db.scalars(statement.order_by(CompanyModel.created_at.desc())))


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)) -> CompanyModel:
    existing = db.scalar(select(CompanyModel).where(CompanyModel.tax_id == payload.tax_id))
    if existing:
        existing.legal_name = payload.legal_name
        existing.address = payload.address
        existing.phone = payload.phone
        db.commit()
        db.refresh(existing)
        return existing

    company = CompanyModel(**payload.model_dump())
    db.add(company)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        existing = db.scalar(select(CompanyModel).where(CompanyModel.tax_id == payload.tax_id))
        if existing:
            return existing
        raise HTTPException(status_code=409, detail="Ya existe una empresa con este NIT") from exc
    db.refresh(company)
    return company


@router.get("/{company_id}/contacts", response_model=list[ContactRead])
def list_contacts(company_id: UUID, db: Session = Depends(get_db)) -> list[ContactModel]:
    return list(db.scalars(select(ContactModel).where(ContactModel.company_id == company_id)))


@router.post("/{company_id}/contacts", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(
    company_id: UUID,
    payload: ContactCreate,
    db: Session = Depends(get_db),
) -> ContactModel:
    if db.get(CompanyModel, company_id) is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    contact = ContactModel(company_id=company_id, **payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact
