from decimal import Decimal

from sqlalchemy.orm import Session

from src.application.dto.schemas import QuotationCreate
from src.application.use_cases.quotations import QuotationUseCases
from src.domain.entities.enums import QuotationStatus
from src.infrastructure.database.models import ClientModel


def test_create_and_approve_quotation(db_session: Session) -> None:
    client = ClientModel(
        name="Pacific Trading Ltda.",
        tax_id="830123456-1",
        email="logistica@pacific.com",
    )
    db_session.add(client)
    db_session.commit()

    payload = QuotationCreate(
        client_id=client.id,
        origin_port="Ningbo",
        destination_port="Buenaventura",
        cargo_description="Repuestos industriales paletizados",
        incoterm="FOB",
        estimated_cost=Decimal("2450.00"),
        currency="USD",
    )

    use_cases = QuotationUseCases(db_session)
    quotation = use_cases.create(payload)
    approved = use_cases.approve(quotation.id)

    assert quotation.client_id == client.id
    assert approved.status == QuotationStatus.APPROVED.value
    assert approved.decided_at is not None
