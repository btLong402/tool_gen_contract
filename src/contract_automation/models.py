from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TemplateItem:
    id: int
    name: str
    file_path: str
    tags: list[str]
    created_at: str


@dataclass(slots=True)
class RecordItem:
    id: int
    template_id: int
    input_data: dict[str, Any]
    output_docx_path: str | None
    output_pdf_path: str | None
    partner_key: str | None
    is_draft: bool
    created_at: str
