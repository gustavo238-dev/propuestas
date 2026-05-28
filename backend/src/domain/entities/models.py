from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from src.domain.entities.enums import CargoStatus, ShipmentType


@dataclass(frozen=True)
class Client:
    id: UUID
    name: str
    tax_id: str
    email: str
    phone: str | None


@dataclass(frozen=True)
class Quotation:
    id: UUID
    client_id: UUID
    origin_port: str
    destination_port: str
    cargo_description: str
    incoterm: str
    estimated_cost: Decimal | None
    currency: str


@dataclass(frozen=True)
class Shipment:
    id: UUID
    client_id: UUID
    shipment_type: ShipmentType
    mbl_number: str
    vessel_name: str
    origin_port: str
    destination_port: str
    eta: date | None
    dta: date | None
    cargo_status: CargoStatus
    goods_description: str
    created_at: datetime
