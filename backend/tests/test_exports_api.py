from io import BytesIO

from openpyxl import load_workbook


def test_export_shipments_xlsx_returns_workbook(client) -> None:
    payload = [
        {
            "mbl_number": "MAEU9283712",
            "client": "Andes Import S.A.S.",
            "origin_port": "Shanghai",
            "destination_port": "Cartagena",
            "eta": "2026-06-14",
            "dta": "2026-06-16",
            "cargo_status": "IN_TRANSIT",
        }
    ]

    response = client.post("/api/v1/exports/shipments/xlsx", json=payload)

    assert response.status_code == 200
    assert response.content
    workbook = load_workbook(BytesIO(response.content))
    sheet = workbook.active
    assert sheet["A1"].value == "MBL"
    assert sheet["A2"].value == "MAEU9283712"
