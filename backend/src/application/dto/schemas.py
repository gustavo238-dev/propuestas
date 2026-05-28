from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.domain.entities.enums import (
    CargoStatus,
    DocumentStatus,
    DocumentType,
    QuotationStatus,
    ShipmentType,
    UserRole,
)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool


class ClientCreate(BaseModel):
    company_id: UUID | None = None
    name: str = Field(min_length=2)
    tax_id: str
    email: EmailStr
    phone: str | None = None
    status: str = "ACTIVE"


class CompanyCreate(BaseModel):
    legal_name: str
    tax_id: str
    address: str | None = None
    phone: str | None = None


class CompanyRead(CompanyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class ContactCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    position: str | None = None


class ContactRead(ContactCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID


class ClientRead(ClientCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class QuotationCreate(BaseModel):
    client_id: UUID
    origin_port: str
    destination_port: str
    cargo_description: str
    incoterm: str
    estimated_cost: Decimal | None = None
    currency: str = "USD"


class QuotationRead(QuotationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: QuotationStatus
    created_at: datetime
    decided_at: datetime | None = None


class ContainerCreate(BaseModel):
    container_number: str
    container_type: str
    seal_number: str | None = None
    weight_kg: Decimal | None = None
    status: str = "CREATED"


class ContainerRead(ContainerCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class HblCreate(BaseModel):
    hbl_number: str
    consignee: str | None = None
    notify_party: str | None = None
    goods_description: str | None = None


class HblRead(HblCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class ShipmentCreate(BaseModel):
    client_id: UUID
    quotation_id: UUID | None = None
    carrier_id: UUID | None = None
    shipment_type: ShipmentType
    mbl_number: str
    vessel_name: str
    origin_port: str
    destination_port: str
    eta: date | None = None
    dta: date | None = None
    cargo_status: CargoStatus = CargoStatus.CREATED
    goods_description: str
    containers: list[ContainerCreate] = []
    hbls: list[HblCreate] = []


class ShipmentRead(ShipmentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    containers: list[ContainerRead] = []
    hbls: list[HblRead] = []


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    shipment_id: UUID | None
    document_type: DocumentType
    file_name: str
    storage_path: str
    status: DocumentStatus
    created_at: datetime


class OcrExtractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    raw_text: str
    extracted_data: dict
    confidence: Decimal | None
    validation_status: str
    created_at: datetime


class PdfGeneratedRead(BaseModel):
    document: DocumentRead
    download_url: str


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject: str
    body: str
    status: str
    created_at: datetime
