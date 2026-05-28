from pathlib import Path

from src.domain.entities.enums import DocumentType
from src.infrastructure.ocr.tesseract_service import TesseractOcrService
from src.infrastructure.pdf.reportlab_service import ReportLabPdfService


def test_ocr_extracts_maritime_fields_from_text() -> None:
    service = TesseractOcrService()
    text = """
    CLIENTE: Andes Import S.A.S.
    NAVIERA: Maersk
    MBL: MAEU9283712
    HBL: HBL-CO-88421
    ETA: 2026-06-14
    DTA: 2026-06-16
    MERCANCIA: Repuestos industriales
    Contenedor MSCU1234567
    """

    extracted = service._extract_maritime_fields(text)

    assert extracted["mbl"] == "MAEU9283712"
    assert extracted["hbl"] == "HBL-CO-88421"
    assert extracted["eta"] == "2026-06-14"
    assert extracted["dta"] == "2026-06-16"
    assert extracted["containers"] == ["MSCU1234567"]


def test_reportlab_pdf_service_creates_business_pdf(tmp_path: Path) -> None:
    output_path = tmp_path / "factura.pdf"

    generated_path = ReportLabPdfService().generate_business_pdf(
        title=DocumentType.INVOICE.value,
        payload={
            "cliente": "Andes Import S.A.S.",
            "mbl": "MAEU9283712",
            "estado": "En transito",
        },
        output_path=output_path,
    )

    assert generated_path.exists()
    assert generated_path.stat().st_size > 0
