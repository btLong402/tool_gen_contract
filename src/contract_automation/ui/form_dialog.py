from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from contract_automation.data.database import Database
from contract_automation.services.export_service import build_output_docx_name, convert_docx_to_pdf
from contract_automation.services.template_service import render_contract


class DynamicFormDialog(QDialog):
    PARTNER_KEY_CANDIDATES = ["partner_key", "partner_name", "doi_tac", "ten_doi_tac"]

    def __init__(
        self,
        db: Database,
        template_id: int,
        template_name: str,
        template_path: Path,
        tags: list[str],
        initial_data: dict[str, str] | None = None,
        editing_record_id: int | None = None,
        export_dir: Path | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.template_id = template_id
        self.template_name = template_name
        self.template_path = template_path
        self.tags = sorted(tags)
        self.initial_data = initial_data or {}
        self.editing_record_id = editing_record_id
        self.export_dir = export_dir or Path.home() / "exports"
        self.inputs: dict[str, QLineEdit] = {}

        self.setWindowTitle(f"📝 Fill template: {template_name}")
        self.setModal(True)
        self.resize(750, 600)
        self.setStyleSheet(self._get_stylesheet())

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title = QLabel(f"Template: {self.template_name}")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        info = QLabel("Fill in the required fields below, then export or save as draft.")
        info.setStyleSheet("color: #666; font-size: 11px;")
        info.setWordWrap(True)
        header_layout.addWidget(info)

        layout.addLayout(header_layout)

        # Form fields section
        scroll = QScrollArea()
        scroll.setObjectName("formScroll")
        scroll.setWidgetResizable(True)
        
        form_container = QWidget()
        form_container.setObjectName("formContainer")
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(8, 8, 8, 8)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        for tag in self.tags:
            label = QLabel(f"{tag}:")
            label.setMinimumWidth(100)
            
            edit = QLineEdit()
            edit.setObjectName("formInput")
            edit.setPlaceholderText(f"Enter {tag}...")
            edit.setMinimumHeight(32)
            
            if tag in self.initial_data:
                edit.setText(str(self.initial_data[tag]))
            
            self.inputs[tag] = edit
            form_layout.addRow(label, edit)

        scroll.setWidget(form_container)
        layout.addWidget(scroll)

        # Options section
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)

        self.export_pdf_checkbox = QCheckBox("📄 Export PDF after DOCX")
        self.export_pdf_checkbox.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        options_layout.addWidget(self.export_pdf_checkbox)
        options_layout.addStretch()

        layout.addLayout(options_layout)

        # Button section
        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        self.load_profile_btn = QPushButton("👤 Load partner profile")
        self.load_profile_btn.setObjectName("secondaryButton")
        self.load_profile_btn.setMinimumHeight(36)
        self.load_profile_btn.clicked.connect(self._load_profile)
        button_row.addWidget(self.load_profile_btn)

        self.save_draft_btn = QPushButton("💾 Save draft")
        self.save_draft_btn.setObjectName("warningButton")
        self.save_draft_btn.setMinimumHeight(36)
        self.save_draft_btn.clicked.connect(self._save_draft)
        button_row.addWidget(self.save_draft_btn)

        self.export_btn = QPushButton("✅ Export contract")
        self.export_btn.setObjectName("primaryButton")
        self.export_btn.setMinimumHeight(36)
        self.export_btn.clicked.connect(self._export_contract)
        button_row.addWidget(self.export_btn)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(self.cancel_btn)

        layout.addLayout(button_row)

    def _get_stylesheet(self) -> str:
        return """
            QDialog {
                background-color: #f5f5f5;
            }

            #formScroll {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }

            #formContainer {
                background-color: white;
            }

            QLabel {
                color: #2c3e50;
            }

            #formInput {
                background-color: #fafafa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px 8px;
                color: #2c3e50;
                selection-background-color: #3498db;
            }

            #formInput:focus {
                border: 2px solid #3498db;
                background-color: white;
            }

            #formInput::placeholder {
                color: #999;
            }

            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 500;
                font-size: 12px;
                cursor: pointer;
                background-color: #ecf0f1;
                color: #2c3e50;
            }

            QPushButton:hover {
                background-color: #d5dbdb;
            }

            QPushButton:pressed {
                background-color: #bdc3c7;
            }

            #primaryButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
            }

            #primaryButton:hover {
                background-color: #229954;
            }

            #primaryButton:pressed {
                background-color: #1e8449;
            }

            #secondaryButton {
                background-color: #3498db;
                color: white;
            }

            #secondaryButton:hover {
                background-color: #2980b9;
            }

            #secondaryButton:pressed {
                background-color: #1f618d;
            }

            #warningButton {
                background-color: #f39c12;
                color: white;
            }

            #warningButton:hover {
                background-color: #e67e22;
            }

            #warningButton:pressed {
                background-color: #d35400;
            }

            #cancelButton {
                background-color: #95a5a6;
                color: white;
            }

            #cancelButton:hover {
                background-color: #7f8c8d;
            }

            #cancelButton:pressed {
                background-color: #5d6d7b;
            }
        """

    def _collect_input_data(self) -> dict[str, str]:
        return {key: widget.text().strip() for key, widget in self.inputs.items()}

    def _find_partner_key(self, data: dict[str, str]) -> str | None:
        for key in self.PARTNER_KEY_CANDIDATES:
            value = data.get(key, "").strip()
            if value:
                return value
        return None

    def _load_profile(self) -> None:
        data = self._collect_input_data()
        partner_key = self._find_partner_key(data)
        if not partner_key:
            QMessageBox.information(
                self,
                "Missing partner key",
                "Fill one of these fields first: partner_key, partner_name, doi_tac, ten_doi_tac.",
            )
            return

        profile = self.db.get_profile(partner_key)
        if not profile:
            QMessageBox.information(self, "Not found", f"No profile for partner '{partner_key}'.")
            return

        for tag, value in profile.items():
            if tag in self.inputs and not self.inputs[tag].text().strip():
                self.inputs[tag].setText(str(value))

        QMessageBox.information(self, "Loaded", "Partner profile data loaded into empty fields.")

    def _save_draft(self) -> None:
        data = self._collect_input_data()
        partner_key = self._find_partner_key(data)

        if self.editing_record_id is not None:
            self.db.update_record(
                record_id=self.editing_record_id,
                input_data=data,
                output_docx_path=None,
                output_pdf_path=None,
                partner_key=partner_key,
                is_draft=True,
            )
        else:
            self.db.create_record(
                template_id=self.template_id,
                input_data=data,
                output_docx_path=None,
                output_pdf_path=None,
                partner_key=partner_key,
                is_draft=True,
            )

        if partner_key:
            self.db.upsert_profile(partner_key, data)

        QMessageBox.information(self, "Draft saved", "The draft has been saved successfully.")

    def _export_contract(self) -> None:
        data = self._collect_input_data()
        if not any(value for value in data.values()):
            QMessageBox.warning(self, "Empty form", "Please fill at least one field before export.")
            return

        output_docx_name = build_output_docx_name(self.template_name)
        output_docx_path = self.export_dir / output_docx_name

        try:
            render_contract(self.template_path, data, output_docx_path)
        except Exception as exc:
            message = f"Cannot render contract:\n{exc}"
            if "unexpected char '\\'" in str(exc):
                message += (
                    "\n\nTip: check template tags in Word. "
                    "If a tag looks like {{ten\\_bien}}, change it to {{ten_bien}}."
                )
            QMessageBox.critical(self, "Export failed", message)
            return

        output_pdf_path: Path | None = None
        if self.export_pdf_checkbox.isChecked():
            candidate = output_docx_path.with_suffix(".pdf")
            success = convert_docx_to_pdf(output_docx_path, candidate)
            if success:
                output_pdf_path = candidate
            else:
                QMessageBox.warning(
                    self,
                    "PDF conversion",
                    "DOCX export succeeded but PDF conversion failed. Check Word/docx2pdf setup.",
                )

        partner_key = self._find_partner_key(data)
        if self.editing_record_id is not None:
            self.db.update_record(
                record_id=self.editing_record_id,
                input_data=data,
                output_docx_path=str(output_docx_path),
                output_pdf_path=str(output_pdf_path) if output_pdf_path else None,
                partner_key=partner_key,
                is_draft=False,
            )
        else:
            self.db.create_record(
                template_id=self.template_id,
                input_data=data,
                output_docx_path=str(output_docx_path),
                output_pdf_path=str(output_pdf_path) if output_pdf_path else None,
                partner_key=partner_key,
                is_draft=False,
            )

        if partner_key:
            self.db.upsert_profile(partner_key, data)

        QMessageBox.information(self, "Exported", f"Contract exported to:\n{output_docx_path}")
        self.accept()
