from sqlalchemy.orm import Session

from src.infrastructure.database.models import ClientModel


def test_create_shipment_with_container_and_hbl(client, db_session: Session) -> None:
    account = ClientModel(
        name="Grupo Norte Importador",
        tax_id="901222333-4",
        email="importaciones@gruponorte.com",
    )
    db_session.add(account)
    db_session.commit()

    payload = {
        "client_id": str(account.id),
        "shipment_type": "CONSOLIDATED",
        "mbl_number": "HLCU7719200",
        "vessel_name": "Hapag Bremen",
        "origin_port": "Ningbo",
        "destination_port": "Buenaventura",
        "eta": "2026-06-22",
        "dta": "2026-06-24",
        "cargo_status": "DOCUMENT_REVIEW",
        "goods_description": "Carga consolidada de importacion",
        "containers": [
            {
                "container_number": "MSCU1234567",
                "container_type": "40HC",
                "seal_number": "SL-8892",
                "weight_kg": "18500.00",
                "status": "IN_TRANSIT",
            }
        ],
        "hbls": [
            {
                "hbl_number": "HBL-CO-99118",
                "consignee": "Grupo Norte Importador",
                "notify_party": "Agente Aduanero",
                "goods_description": "Partes electricas",
            }
        ],
    }

    response = client.post("/api/v1/shipments", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["mbl_number"] == payload["mbl_number"]
    assert body["shipment_type"] == "CONSOLIDATED"
    assert body["containers"][0]["container_number"] == "MSCU1234567"
    assert body["hbls"][0]["hbl_number"] == "HBL-CO-99118"
