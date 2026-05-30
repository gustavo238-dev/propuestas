def test_create_and_list_clients(client) -> None:
    payload = {
        "name": "Andes Import S.A.S.",
        "tax_id": "900123456-7",
        "email": "operaciones@andesimport.com",
        "phone": "+57 601 555 0101",
        "status": "ACTIVE",
    }

    create_response = client.post("/api/v1/clients", json=payload)
    list_response = client.get("/api/v1/clients")

    assert create_response.status_code == 201
    assert create_response.json()["name"] == payload["name"]
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
