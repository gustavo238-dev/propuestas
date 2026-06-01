from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import logging
from pathlib import Path

from src.application.use_cases.pdf_documents import PdfDocumentUseCases
from src.application.use_cases.documents import DocumentUseCases
from src.domain.entities.enums import DocumentType
from src.infrastructure.email.smtp_service import SmtpEmailService
from src.infrastructure.database.models import ClientModel, CarrierModel
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
def create_shipment(payload: ShipmentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> ShipmentModel:
    data = payload.model_dump(exclude={"containers", "hbls"})
    shipment = ShipmentModel(**data)
    shipment.containers = [ContainerModel(**item.model_dump()) for item in payload.containers]
    shipment.hbls = [HblModel(**item.model_dump()) for item in payload.hbls]
    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    # Generar factura (INVOICE) asociada al embarque y registrarla
    try:
        # Construir payload completo para la factura
        carrier = None
        if shipment.carrier_id:
            try:
                carrier_obj = db.get(CarrierModel, shipment.carrier_id)
                carrier = carrier_obj.name if carrier_obj is not None else None
            except Exception:
                carrier = None

        pdf_payload = {
            "shipment_id": str(shipment.id),
            "mbl": shipment.mbl_number or "No detectado",
            "vessel": shipment.vessel_name or "No detectado",
            "eta": shipment.eta.isoformat() if getattr(shipment, "eta", None) else "No detectado",
            "dta": shipment.dta.isoformat() if getattr(shipment, "dta", None) else "No detectado",
            "hbls": [h.hbl_number for h in shipment.hbls] if shipment.hbls else [],
            "containers": [c.container_number for c in shipment.containers] if shipment.containers else [],
            "goods": shipment.goods_description or "No detectado",
            "origin": shipment.origin_port or "No detectado",
            "destination": shipment.destination_port or "No detectado",
            "client": (db.get(ClientModel, shipment.client_id).name if shipment.client_id and db.get(ClientModel, shipment.client_id) else str(shipment.client_id)),
            "carrier": carrier or "No detectado",
        }
        path = PdfDocumentUseCases().generate(DocumentType.INVOICE, pdf_payload)
        document = DocumentUseCases(db).register_generated(path, DocumentType.INVOICE, shipment.id)

        # Enviar email al cliente en background si tiene email
        try:
            client = db.get(ClientModel, shipment.client_id) if shipment.client_id else None
            if client is not None and getattr(client, "email", None):
                subject = f"Factura de embarque {shipment.mbl_number}"
                html_body = f"<p>Adjunto encontrará la factura de embarque para el MBL <strong>{shipment.mbl_number}</strong>.</p>"
                attachment_path = Path(document.storage_path)
                background_tasks.add_task(
                    SmtpEmailService().send_html_email,
                    [client.email],
                    subject,
                    html_body,
                    [attachment_path],
                )
        except Exception:
            logging.exception("Error programando envio de email con factura al crear embarque")
    except Exception:
        logging.exception("Error generando o registrando factura al crear embarque")

    return shipment


@router.get("/{shipment_id}", response_model=ShipmentRead)
def get_shipment(shipment_id: UUID, db: Session = Depends(get_db)) -> ShipmentModel:
    shipment = db.get(ShipmentModel, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Embarque no encontrado")
    return shipment
