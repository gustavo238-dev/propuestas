from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class ReportLabPdfService:
    def generate_business_pdf(self, title: str, payload: dict, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        document = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Empresa Logistica Maritima", styles["Title"]),
            Paragraph(title, styles["Heading2"]),
            Spacer(1, 18),
        ]

        rows = [["Campo", "Valor"]]
        rows.extend([self._humanize(key), str(value)] for key, value in payload.items())
        table = Table(rows, colWidths=[160, 330])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
        document.build(story)
        return output_path

    @staticmethod
    def _humanize(value: str) -> str:
        return value.replace("_", " ").title()
