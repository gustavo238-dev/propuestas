import uuid
from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.enums import (
    CargoStatus,
    DocumentStatus,
    DocumentType,
    NotificationStatus,
    QuotationStatus,
    ShipmentType,
    UserRole,
)
from src.infrastructure.database.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserModel(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(40), default=UserRole.CLIENT.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CompanyModel(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    legal_name: Mapped[str] = mapped_column(String(180))
    tax_id: Mapped[str] = mapped_column(String(80), unique=True)
    address: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(60))
    clients: Mapped[list["ClientModel"]] = relationship(back_populates="company")


class ContactModel(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(60))
    position: Mapped[str | None] = mapped_column(String(100))


class ClientModel(Base, TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("companies.id"))
    name: Mapped[str] = mapped_column(String(180))
    tax_id: Mapped[str] = mapped_column(String(80), index=True)
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    company: Mapped[CompanyModel | None] = relationship(back_populates="clients")


class CarrierModel(Base, TimestampMixin):
    __tablename__ = "carriers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(180), unique=True)
    scac_code: Mapped[str | None] = mapped_column(String(30))


class QuotationModel(Base, TimestampMixin):
    __tablename__ = "quotations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    requested_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    origin_port: Mapped[str] = mapped_column(String(120))
    destination_port: Mapped[str] = mapped_column(String(120))
    cargo_description: Mapped[str] = mapped_column(Text)
    incoterm: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(40), default=QuotationStatus.REQUESTED.value)
    estimated_cost: Mapped[float | None] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime)


class ShipmentModel(Base, TimestampMixin):
    __tablename__ = "shipments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    quotation_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("quotations.id"))
    carrier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("carriers.id"))
    shipment_type: Mapped[str] = mapped_column(String(40), default=ShipmentType.DIRECT.value)
    mbl_number: Mapped[str] = mapped_column(String(80), index=True)
    vessel_name: Mapped[str] = mapped_column(String(140))
    origin_port: Mapped[str] = mapped_column(String(120))
    destination_port: Mapped[str] = mapped_column(String(120))
    eta: Mapped[date | None] = mapped_column(Date)
    dta: Mapped[date | None] = mapped_column(Date)
    cargo_status: Mapped[str] = mapped_column(String(40), default=CargoStatus.CREATED.value)
    goods_description: Mapped[str] = mapped_column(Text)
    containers: Mapped[list["ContainerModel"]] = relationship(cascade="all, delete-orphan")
    hbls: Mapped[list["HblModel"]] = relationship(cascade="all, delete-orphan")


class HblModel(Base):
    __tablename__ = "hbls"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    shipment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("shipments.id"), index=True)
    hbl_number: Mapped[str] = mapped_column(String(80), index=True)
    consignee: Mapped[str | None] = mapped_column(String(180))
    notify_party: Mapped[str | None] = mapped_column(String(180))
    goods_description: Mapped[str | None] = mapped_column(Text)


class ContainerModel(Base):
    __tablename__ = "containers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    shipment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("shipments.id"), index=True)
    container_number: Mapped[str] = mapped_column(String(40), index=True)
    container_type: Mapped[str] = mapped_column(String(40))
    seal_number: Mapped[str | None] = mapped_column(String(60))
    weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(40), default="CREATED")


class DocumentModel(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    shipment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("shipments.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(60), default=DocumentType.EXTERNAL_PDF.value)
    file_name: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(40), default=DocumentStatus.UPLOADED.value)
    uploaded_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))


class OcrExtractionModel(Base, TimestampMixin):
    __tablename__ = "ocr_extractions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    extracted_data: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 2))
    validation_status: Mapped[str] = mapped_column(String(40), default="PENDING")
    validated_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))


class TrackingEventModel(Base, TimestampMixin):
    __tablename__ = "tracking_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    shipment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("shipments.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    event_date: Mapped[datetime] = mapped_column(DateTime)
    location: Mapped[str | None] = mapped_column(String(120))


class NotificationModel(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("clients.id"))
    shipment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("shipments.id"))
    notification_type: Mapped[str] = mapped_column(String(80))
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default=NotificationStatus.PENDING.value)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)


class InvoiceModel(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    shipment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("shipments.id"), index=True)
    invoice_number: Mapped[str] = mapped_column(String(80), unique=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    pdf_document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"))
