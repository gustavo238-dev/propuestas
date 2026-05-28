from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import ShipmentCreate, ShipmentRead
from src.infrastructure.database.models import ContainerModel, HblModel, ShipmentModel
from src.infrastructure.database.session import get_db

router = APIRouter()


@router.get("", response_model=list[ShipmentRead])
def list_shipments(db: Session = Depends(get_db)) -> list[ShipmentModel]:
    return list(db.scalars(select(ShipmentModel).order_by(ShipmentModel.created_at.desc())))


@router.post("", response_model=ShipmentRead, status_code=status.HTTP_201_CREATED)
def create_shipment(payload: ShipmentCreate, db: Session = Depends(get_db)) -> ShipmentModel:
    data = payload.model_dump(exclude={"containers", "hbls"})
    shipment = ShipmentModel(**data)
    shipment.containers = [ContainerModel(**item.model_dump()) for item in payload.containers]
    shipment.hbls = [HblModel(**item.model_dump()) for item in payload.hbls]
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.get("/{shipment_id}", response_model=ShipmentRead)
def get_shipment(shipment_id: UUID, db: Session = Depends(get_db)) -> ShipmentModel:
    shipment = db.get(ShipmentModel, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Embarque no encontrado")
    return shipment
