from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import QuotationCreate, QuotationRead
from src.application.use_cases.quotations import QuotationUseCases
from src.infrastructure.database.models import QuotationModel
from src.infrastructure.database.session import get_db
from src.application.use_cases.pdf_documents import PdfDocumentUseCases
from src.application.use_cases.documents import DocumentUseCases
from src.domain.entities.enums import DocumentType
import logging
from src.infrastructure.database.models import ShipmentModel, ClientModel, ContainerModel, HblModel, CarrierModel
from src.domain.entities.enums import ShipmentType
from uuid import uuid4
from src.infrastructure.email.smtp_service import SmtpEmailService
from pathlib import Path
from src.shared.config.settings import settings

router = APIRouter()


@router.get("", response_model=list[QuotationRead])
def list_quotations(db: Session = Depends(get_db)) -> list[QuotationModel]:
    return list(db.scalars(select(QuotationModel).order_by(QuotationModel.created_at.desc())))


@router.post("", response_model=QuotationRead, status_code=status.HTTP_201_CREATED)
def create_quotation(payload: QuotationCreate, db: Session = Depends(get_db)) -> QuotationModel:
    try:
        quotation = QuotationUseCases(db).create(payload)

        # Generar PDF de la cotizacion y registrarlo en documentos (no bloquear el flujo principal)
        try:
            pdf_payload = {
                "client_id": str(quotation.client_id),
                "origin_port": quotation.origin_port,
                "destination_port": quotation.destination_port,
                "cargo_description": quotation.cargo_description,
                "incoterm": quotation.incoterm,
                "estimated_cost": str(quotation.estimated_cost) if quotation.estimated_cost is not None else None,
            }
            path = PdfDocumentUseCases().generate(DocumentType.QUOTATION, pdf_payload)
            DocumentUseCases(db).register_generated(path, DocumentType.QUOTATION)
        except Exception as exc:
            logging.exception("Error generando/registrando PDF de cotizacion: %s", exc)

        return quotation
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{quotation_id}", response_model=QuotationRead)
def get_quotation(quotation_id: UUID, db: Session = Depends(get_db)) -> QuotationModel:
    quotation = db.get(QuotationModel, quotation_id)
    if quotation is None:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")
    return quotation


@router.post("/{quotation_id}/approve", response_model=QuotationRead)
def approve_quotation(quotation_id: UUID, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> QuotationModel:
    try:
        quotation = QuotationUseCases(db).approve(quotation_id)

        # Al aprobar, crear un embarque minimal y generar la factura de embarque (INVOICE)
        try:
            # Obtener datos del cliente para completar el embarque
            client = db.get(ClientModel, quotation.client_id)
            mbl = f"MBL-{uuid4().hex[:8].upper()}"
            vessel = "Por Asignar"
            shipment = ShipmentModel(
                client_id=quotation.client_id,
                quotation_id=quotation.id,
                shipment_type=ShipmentType.DIRECT.value,
                mbl_number=mbl,
                vessel_name=vessel,
                origin_port=quotation.origin_port,
                destination_port=quotation.destination_port,
                goods_description=quotation.cargo_description,
            )

            # Crear un contenedor y un HBL basicos asociados al embarque
            container = ContainerModel(
                container_number=f"C-{uuid4().hex[:8].upper()}",
                container_type="40HC",
                seal_number=None,
                weight_kg=None,
                status="CREATED",
            )
            hbl = HblModel(
                hbl_number=f"HBL-{uuid4().hex[:8].upper()}",
                consignee=(client.name if client is not None else "Consignatario"),
                notify_party="Agente Aduanero",
                goods_description=quotation.cargo_description,
            )

            shipment.containers = [container]
            shipment.hbls = [hbl]

            db.add(shipment)
            db.commit()
            db.refresh(shipment)

            # Generar PDF de factura de embarque y registrarlo vinculado al embarque
            # Construir payload completo
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
                "client": (client.name if client is not None else str(shipment.client_id)),
                "carrier": carrier or "No detectado",
            }
            path = PdfDocumentUseCases().generate(DocumentType.INVOICE, pdf_payload)
            document = DocumentUseCases(db).register_generated(path, DocumentType.INVOICE, shipment.id)

            # Enviar email con el PDF adjunto al cliente en segundo plano
            try:
                if client is not None and getattr(client, "email", None):
                    subject = f"Factura de embarque {shipment.mbl_number}"
                    html_body = f"<p>Adjunto encontrará la factura de embarque para el MBL <strong>{shipment.mbl_number}</strong>.</p>"
                    attachment_path = Path(document.storage_path)
                    # Usa BackgroundTasks para no bloquear la respuesta
                    background_tasks.add_task(
                        SmtpEmailService().send_html_email,
                        [client.email],
                        subject,
                        html_body,
                        [attachment_path],
                    )
            except Exception:
                logging.exception("Error programando envio de email con factura de embarque")
        except Exception as exc:
            logging.exception("Error creando embarque o generando factura de embarque: %s", exc)

        return quotation
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{quotation_id}/reject", response_model=QuotationRead)
def reject_quotation(quotation_id: UUID, db: Session = Depends(get_db)) -> QuotationModel:
    try:
        return QuotationUseCases(db).reject(quotation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
