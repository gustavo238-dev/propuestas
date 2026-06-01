def test_create_company_api(client) -> None:
    response = client.post(
        "/api/v1/companies",
        json={
            "legal_name": "Pacific Cargo S.A.S.",
            "tax_id": "901555222-1",
            "address": "Cartagena",
            "phone": "+57 300 111 2233",
        },
    )

    assert response.status_code == 201
    assert response.json()["legal_name"] == "Pacific Cargo S.A.S."
    assert response.json()["tax_id"] == "901555222-1"


def test_create_company_with_existing_tax_id_updates_company(client) -> None:
    payload = {
        "legal_name": "Pacific Cargo S.A.S.",
        "tax_id": "901555222-1",
        "address": "Cartagena",
        "phone": "+57 300 111 2233",
    }
    first_response = client.post("/api/v1/companies", json=payload)

    second_response = client.post(
        "/api/v1/companies",
        json={
            **payload,
            "legal_name": "Pacific Cargo Colombia S.A.S.",
            "address": "Chapinero",
        },
    )

    assert second_response.status_code == 201
    assert second_response.json()["id"] == first_response.json()["id"]
    assert second_response.json()["legal_name"] == "Pacific Cargo Colombia S.A.S."
    assert second_response.json()["address"] == "Chapinero"


def test_list_companies_can_filter_by_tax_id(client) -> None:
    client.post(
        "/api/v1/companies",
        json={
            "legal_name": "Pacific Cargo S.A.S.",
            "tax_id": "901555222-1",
            "address": "Cartagena",
            "phone": "+57 300 111 2233",
        },
    )

    response = client.get("/api/v1/companies?tax_id=901555222-1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["tax_id"] == "901555222-1"
