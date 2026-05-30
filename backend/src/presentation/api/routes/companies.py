from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import CompanyCreate, CompanyRead, ContactCreate, ContactRead
from src.infrastructure.database.models import CompanyModel, ContactModel
from src.infrastructure.database.session import get_db

router = APIRouter()


@router.get("", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)) -> list[CompanyModel]:
    return list(db.scalars(select(CompanyModel).order_by(CompanyModel.created_at.desc())))


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)) -> CompanyModel:
    company = CompanyModel(**payload.model_dump())
    db.add(company)
    db.commit()
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
