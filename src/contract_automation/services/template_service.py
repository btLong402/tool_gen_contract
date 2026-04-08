from __future__ import annotations

import re
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path

from docxtpl import DocxTemplate

TAG_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_\\\.]+)\s*}}")
JINJA_BLOCK_PATTERNS = (
    re.compile(r"{{.*?}}", re.DOTALL),
    re.compile(r"{%.*?%}", re.DOTALL),
    re.compile(r"{#.*?#}", re.DOTALL),
)


def _normalize_tag_name(tag: str) -> str:
    return tag.replace("\\_", "_").replace("\\.", ".").strip()


def _cleanup_escaped_chars_in_jinja_blocks(xml_text: str) -> str:
    cleaned = xml_text
    for pattern in JINJA_BLOCK_PATTERNS:
        cleaned = pattern.sub(lambda m: m.group(0).replace("\\_", "_").replace("\\.", "."), cleaned)
    return cleaned


def _create_repaired_docx_with_clean_jinja(template_path: Path) -> Path:
    temp_file = tempfile.NamedTemporaryFile(prefix="repaired_template_", suffix=".docx", delete=False)
    temp_file_path = Path(temp_file.name)
    temp_file.close()

    with zipfile.ZipFile(template_path, "r") as src_zip, zipfile.ZipFile(temp_file_path, "w") as dst_zip:
        for item in src_zip.infolist():
            content = src_zip.read(item.filename)
            if item.filename.startswith("word/") and item.filename.endswith(".xml"):
                xml_text = content.decode("utf-8", errors="ignore")
                xml_text = _cleanup_escaped_chars_in_jinja_blocks(xml_text)
                content = xml_text.encode("utf-8")
            dst_zip.writestr(item, content)

    return temp_file_path


def scan_template_tags(template_path: Path) -> list[str]:
    """Extract jinja variable names from a docx template."""
    tags: set[str] = set()

    try:
        tpl = DocxTemplate(str(template_path))
        discovered = tpl.get_undeclared_template_variables()
        tags.update(_normalize_tag_name(str(item)) for item in discovered)
    except Exception:
        pass

    # Fallback regex scan to handle edge templates where parser misses text.
    try:
        with zipfile.ZipFile(template_path, "r") as docx_zip:
            for name in docx_zip.namelist():
                if not name.startswith("word/") or not name.endswith(".xml"):
                    continue
                xml_text = docx_zip.read(name).decode("utf-8", errors="ignore")
                tags.update(_normalize_tag_name(raw) for raw in TAG_PATTERN.findall(xml_text))
    except Exception:
        pass

    return sorted(tag for tag in tags if tag)


def copy_template_to_storage(source_path: Path, storage_dir: Path) -> Path:
    unique_name = f"{uuid.uuid4().hex}_{source_path.name}"
    target_path = storage_dir / unique_name
    shutil.copy2(source_path, target_path)
    return target_path


def render_contract(template_path: Path, data: dict[str, str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        tpl = DocxTemplate(str(template_path))
        tpl.render(data)
        tpl.save(str(output_path))
        return
    except Exception as exc:
        if "unexpected char '\\\\'" not in str(exc):
            raise

    repaired_path = _create_repaired_docx_with_clean_jinja(template_path)
    try:
        repaired_tpl = DocxTemplate(str(repaired_path))
        repaired_tpl.render(data)
        repaired_tpl.save(str(output_path))
    finally:
        repaired_path.unlink(missing_ok=True)
