from __future__ import annotations

from datetime import datetime
from pathlib import Path

from docx2pdf import convert


def build_output_docx_name(template_name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in template_name)
    return f"{safe}_{timestamp}.docx"


def convert_docx_to_pdf(docx_path: Path, output_pdf_path: Path) -> bool:
    try:
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        convert(str(docx_path), str(output_pdf_path))
        return output_pdf_path.exists()
    except Exception:
        return False
