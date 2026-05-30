import re
from pathlib import Path

import pdfplumber


class TesseractOcrService:
    """Extracts text from digital PDFs and maps maritime fields with deterministic patterns."""

    def extract(self, pdf_path: Path) -> tuple[str, dict, float | None]:
        text_parts: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")

        raw_text = "\n".join(text_parts)
        return raw_text, self._extract_maritime_fields(raw_text), None

    def _extract_maritime_fields(self, text: str) -> dict[str, str | list[str] | None]:
        return {
            "mbl": self._match(text, r"\bMBL[:\s-]+([A-Z0-9-]+)"),
            "hbl": self._match(text, r"\bHBL[:\s-]+([A-Z0-9-]+)"),
            "eta": self._match(text, r"\bETA[:\s-]+([0-9]{2,4}[-/][0-9]{1,2}[-/][0-9]{1,4})"),
            "dta": self._match(text, r"\bDTA[:\s-]+([0-9]{2,4}[-/][0-9]{1,2}[-/][0-9]{1,4})"),
            "containers": re.findall(r"\b[A-Z]{4}[0-9]{7}\b", text),
            "carrier": self._match(text, r"(?:NAVIERA|CARRIER)[:\s-]+(.+)"),
            "ports": self._match(text, r"(?:PUERTOS|PORTS)[:\s-]+(.+)"),
            "client": self._match(text, r"(?:CLIENTE|CLIENT)[:\s-]+(.+)"),
            "goods": self._match(text, r"(?:MERCANCIA|GOODS|COMMODITY)[:\s-]+(.+)"),
        }

    @staticmethod
    def _match(text: str, pattern: str) -> str | None:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else None
