from pathlib import Path
from typing import Protocol


class OcrPort(Protocol):
    def extract(self, pdf_path: Path) -> tuple[str, dict, float | None]:
        pass


class PdfGeneratorPort(Protocol):
    def generate_business_pdf(self, title: str, payload: dict, output_path: Path) -> Path:
        pass


class EmailPort(Protocol):
    def send_html_email(
        self,
        recipients: list[str],
        subject: str,
        html_body: str,
        attachments: list[Path] | None = None,
    ) -> None:
        pass
