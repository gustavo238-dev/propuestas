from sqlalchemy.orm import Session

from src.infrastructure.database.models import ClientModel


def test_create_quotation_api(client, db_session: Session) -> None:
    account = ClientModel(
        name="Andes Import S.A.S.",
        tax_id="900123456-7",
        email="operaciones@andesimport.com",
    )
    db_session.add(account)
    db_session.commit()

    response = client.post(
        "/api/v1/quotations",
        json={
            "client_id": str(account.id),
            "origin_port": "Shanghai",
            "destination_port": "Cartagena",
            "cargo_description": "Repuestos industriales",
            "incoterm": "FOB",
            "estimated_cost": None,
            "currency": "USD",
        },
    )

    assert response.status_code == 201
    assert response.json()["client_id"] == str(account.id)
    assert response.json()["status"] == "REQUESTED"


def test_create_quotation_requires_existing_client(client) -> None:
    response = client.post(
        "/api/v1/quotations",
        json={
            "client_id": "00000000-0000-0000-0000-000000000000",
            "origin_port": "Shanghai",
            "destination_port": "Cartagena",
            "cargo_description": "Repuestos industriales",
            "incoterm": "FOB",
            "estimated_cost": None,
            "currency": "USD",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cliente no encontrado para la cotizacion"
