from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.shared.config.settings import settings


def test_upload_and_download_pdf_document(client: TestClient, tmp_path: Path) -> None:
    settings.storage_root = str(tmp_path)
    pdf_content = b"%PDF-1.4\n% test pdf\n"

    upload_response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("mbl.pdf", pdf_content, "application/pdf")},
        data={"document_type": "EXTERNAL_PDF"},
    )

    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]

    download_response = client.get(f"/api/v1/documents/{document_id}/download")

    assert download_response.status_code == 200
    assert download_response.content == pdf_content


def test_generate_and_store_invoice_pdf(
    client: TestClient,
    db_session: Session,
    tmp_path: Path,
) -> None:
    settings.storage_root = str(tmp_path)
    payload = {
        "cliente": "Andes Import S.A.S.",
        "mbl": "MAEU9283712",
        "hbl": "HBL-CO-88421",
        "motonave": "Maersk Cartagena",
        "origen": "Shanghai",
        "destino": "Cartagena",
        "eta": "2026-06-14",
        "dta": "2026-06-16",
        "mercancia": "Repuestos industriales",
        "estado": "En transito",
        "valor": "Pendiente de liquidacion",
    }

    response = client.post("/api/v1/pdf/invoices/store", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["document"]["document_type"] == "INVOICE"
    assert body["download_url"].startswith("/api/v1/documents/")

    download_response = client.get(body["download_url"])
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
