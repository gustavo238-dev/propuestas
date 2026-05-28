from io import BytesIO

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

router = APIRouter()


@router.post("/shipments/xlsx")
def export_shipments_xlsx(payload: list[dict]) -> StreamingResponse:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Embarques"
    headers = ["MBL", "Cliente", "Origen", "Destino", "ETA", "DTA", "Estado"]
    sheet.append(headers)
    for item in payload:
        sheet.append(
            [
                item.get("mbl_number"),
                item.get("client"),
                item.get("origin_port"),
                item.get("destination_port"),
                item.get("eta"),
                item.get("dta"),
                item.get("cargo_status"),
            ]
        )

    stream = BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=embarques.xlsx"},
    )


@router.post("/documents/pdf-to-xlsx")
def export_pdf_extraction_xlsx(payload: dict) -> StreamingResponse:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Extraccion OCR"
    sheet.append(["Campo", "Valor"])
    for key, value in payload.items():
        sheet.append([key, str(value)])

    stream = BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=extraccion_ocr.xlsx"},
    )
