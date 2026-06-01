from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import ClientCreate, ClientRead
from src.infrastructure.database.models import ClientModel
from src.infrastructure.database.session import get_db

router = APIRouter()


@router.get("", response_model=list[ClientRead])
def list_clients(email: str | None = None, db: Session = Depends(get_db)) -> list[ClientModel]:
    statement = select(ClientModel)
    if email:
        statement = statement.where(ClientModel.email == email)
    return list(db.scalars(statement.order_by(ClientModel.created_at.desc())))


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)) -> ClientModel:
    client = ClientModel(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: UUID, db: Session = Depends(get_db)) -> ClientModel:
    client = db.get(ClientModel, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client


@router.put("/{client_id}", response_model=ClientRead)
def update_client(client_id: UUID, payload: ClientCreate, db: Session = Depends(get_db)) -> ClientModel:
    client = db.get(ClientModel, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for field, value in payload.model_dump().items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: UUID, db: Session = Depends(get_db)) -> None:
    client = db.get(ClientModel, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(client)
    db.commit()
