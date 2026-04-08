from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from contract_automation.config import TEMPLATES_DIR, save_exports_dir, load_exports_dir
from contract_automation.data.database import Database
from contract_automation.models import RecordItem, TemplateItem
from contract_automation.services.template_service import copy_template_to_storage, scan_template_tags
from contract_automation.ui.form_dialog import DynamicFormDialog


class MainWindow(QMainWindow):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        self.templates: list[TemplateItem] = []
        self.records: list[RecordItem] = []
        self.export_dir = load_exports_dir()

        self.setWindowTitle("Contract Automation Desktop App")
        self.setMinimumSize(1200, 700)
        self.resize(1200, 700)

        self._build_ui()
        self._reload_templates()

    def _build_ui(self) -> None:
        central = QWidget()
        central.setStyleSheet(self._get_stylesheet())
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header section - Settings bar
        header = self._create_header()
        root.addWidget(header)

        # Main content area
        content = QHBoxLayout()
        content.setContentsMargins(16, 16, 16, 16)
        content.setSpacing(16)

        # Left panel - Templates
        left_panel = self._create_left_panel()
        content.addLayout(left_panel, stretch=3)

        # Right panel - History
        right_panel = self._create_right_panel()
        content.addLayout(right_panel, stretch=2)

        root.addLayout(content)
        self.setCentralWidget(central)

    def _create_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(60)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        title = QLabel("📋 Contract Automation")
        font = title.font()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        layout.addStretch()

        # Export directory selector
        export_label = QLabel("Export to:")
        layout.addWidget(export_label)

        self.export_path_label = QLabel(str(self.export_dir))
        self.export_path_label.setMaximumWidth(300)
        self.export_path_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.export_path_label)

        self.select_dir_btn = QPushButton("📁 Change")
        self.select_dir_btn.setMaximumWidth(100)
        self.select_dir_btn.setObjectName("smallButton")
        self.select_dir_btn.clicked.connect(self._select_export_dir)
        layout.addWidget(self.select_dir_btn)

        return header

    def _create_left_panel(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Title
        title = QLabel("Templates Library")
        font = title.font()
        font.setPointSize(11)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Template list
        self.template_list = QListWidget()
        self.template_list.setObjectName("templateList")
        self.template_list.currentRowChanged.connect(self._reload_records)
        layout.addWidget(self.template_list)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.add_template_btn = QPushButton("➕ Add template")
        self.add_template_btn.setObjectName("primaryButton")
        self.add_template_btn.clicked.connect(self._add_template)
        actions.addWidget(self.add_template_btn)

        self.delete_template_btn = QPushButton("🗑 Delete")
        self.delete_template_btn.setObjectName("dangerButton")
        self.delete_template_btn.clicked.connect(self._delete_selected_template)
        actions.addWidget(self.delete_template_btn)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setObjectName("secondaryButton")
        self.refresh_btn.clicked.connect(self._reload_templates)
        actions.addWidget(self.refresh_btn)

        layout.addLayout(actions)

        # Form and draft buttons
        self.use_template_btn = QPushButton("📝 Open dynamic form")
        self.use_template_btn.setObjectName("actionButton")
        self.use_template_btn.setMinimumHeight(40)
        self.use_template_btn.clicked.connect(self._open_form)
        layout.addWidget(self.use_template_btn)

        self.open_draft_btn = QPushButton("📄 Open selected draft")
        self.open_draft_btn.setObjectName("actionButton")
        self.open_draft_btn.setMinimumHeight(40)
        self.open_draft_btn.clicked.connect(self._open_selected_draft)
        layout.addWidget(self.open_draft_btn)

        return layout

    def _create_right_panel(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Title
        title = QLabel("Draft/Export History")
        font = title.font()
        font.setPointSize(11)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Record list
        self.record_list = QListWidget()
        self.record_list.setObjectName("recordList")
        layout.addWidget(self.record_list)

        return layout

    def _get_stylesheet(self) -> str:
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }

            #header {
                background-color: #2c3e50;
                border-bottom: 2px solid #34495e;
            }

            #header QLabel {
                color: white;
            }

            #header QLabel:last-child {
                color: #bdc3c7;
            }

            QListWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 0px;
                selection-background-color: #3498db;
            }

            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }

            QListWidget::item:hover {
                background-color: #ecf0f1;
            }

            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }

            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 500;
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
                background-color: #3498db;
                color: white;
            }

            #primaryButton:hover {
                background-color: #2980b9;
            }

            #primaryButton:pressed {
                background-color: #1f618d;
            }

            #secondaryButton {
                background-color: #95a5a6;
                color: white;
            }

            #secondaryButton:hover {
                background-color: #7f8c8d;
            }

            #secondaryButton:pressed {
                background-color: #5d6d7b;
            }

            #dangerButton {
                background-color: #e74c3c;
                color: white;
            }

            #dangerButton:hover {
                background-color: #c0392b;
            }

            #dangerButton:pressed {
                background-color: #a93226;
            }

            #actionButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
            }

            #actionButton:hover {
                background-color: #229954;
            }

            #actionButton:pressed {
                background-color: #1e8449;
            }

            #smallButton {
                max-width: 100px;
                padding: 4px 8px;
            }
        """

    def _select_export_dir(self) -> None:
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            str(self.export_dir),
        )
        if not dir_path:
            return

        new_dir = Path(dir_path)
        new_dir.mkdir(parents=True, exist_ok=True)
        
        # Update config and instance variable
        save_exports_dir(new_dir)
        self.export_dir = new_dir
        
        # Update label
        self.export_path_label.setText(str(new_dir))
        self.export_path_label.setToolTip(str(new_dir))
        
        QMessageBox.information(
            self,
            "Directory changed",
            f"Export directory changed to:\n{new_dir}",
        )

    def _selected_template(self) -> TemplateItem | None:
        row = self.template_list.currentRow()
        if row < 0 or row >= len(self.templates):
            return None
        return self.templates[row]

    def _reload_templates(self) -> None:
        self.templates = self.db.list_templates()
        self.template_list.clear()

        for item in self.templates:
            text = f"[{item.id}] {item.name} ({len(item.tags)} tags)"
            self.template_list.addItem(QListWidgetItem(text))

        if self.templates:
            self.template_list.setCurrentRow(0)
        else:
            self.record_list.clear()

    def _reload_records(self) -> None:
        self.record_list.clear()
        selected = self._selected_template()
        if not selected:
            self.records = []
            return

        self.records = self.db.list_records_for_template(selected.id)
        for record in self.records:
            mode = "DRAFT" if record.is_draft else "EXPORTED"
            output_info = record.output_docx_path or "(not exported)"
            text = f"[{record.id}] {mode} | {record.created_at} | {output_info}"
            self.record_list.addItem(QListWidgetItem(text))

    def _selected_record(self) -> RecordItem | None:
        row = self.record_list.currentRow()
        if row < 0 or row >= len(self.records):
            return None
        return self.records[row]

    def _add_template(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Select DOCX template",
            "",
            "Word Template (*.docx)",
        )
        if not path_str:
            return

        source_path = Path(path_str)
        default_name = source_path.stem
        name, accepted = QInputDialog.getText(
            self,
            "Template name",
            "Enter template display name:",
            text=default_name,
        )
        if not accepted or not name.strip():
            return

        tags = scan_template_tags(source_path)
        if not tags:
            confirmation = QMessageBox.question(
                self,
                "No tag found",
                "No `{{...}}` tags found. Import anyway?",
            )
            if confirmation != QMessageBox.StandardButton.Yes:
                return

        copied_path = copy_template_to_storage(source_path, TEMPLATES_DIR)

        try:
            self.db.add_template(name=name.strip(), file_path=str(copied_path), tags=tags)
        except Exception as exc:
            QMessageBox.critical(self, "Import failed", f"Cannot save template:\n{exc}")
            return

        QMessageBox.information(self, "Imported", f"Template imported with {len(tags)} tag(s).")
        self._reload_templates()

    def _delete_selected_template(self) -> None:
        selected = self._selected_template()
        if not selected:
            QMessageBox.information(self, "No selection", "Please select a template first.")
            return

        confirmation = QMessageBox.question(
            self,
            "Delete template",
            f"Delete template '{selected.name}' from library?",
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        self.db.delete_template(selected.id)
        self._reload_templates()

    def _open_form(self) -> None:
        selected = self._selected_template()
        if not selected:
            QMessageBox.information(self, "No selection", "Please select a template first.")
            return

        dialog = DynamicFormDialog(
            db=self.db,
            template_id=selected.id,
            template_name=selected.name,
            template_path=Path(selected.file_path),
            tags=selected.tags,
            export_dir=self.export_dir,
            parent=self,
        )
        dialog.exec()
        self._reload_records()

    def _open_selected_draft(self) -> None:
        selected_template = self._selected_template()
        if not selected_template:
            QMessageBox.information(self, "No selection", "Please select a template first.")
            return

        selected_record = self._selected_record()
        if not selected_record:
            QMessageBox.information(self, "No record", "Please select a draft record in history.")
            return

        if not selected_record.is_draft:
            QMessageBox.information(
                self,
                "Not a draft",
                "The selected record is already exported. Choose a draft record.",
            )
            return

        dialog = DynamicFormDialog(
            db=self.db,
            template_id=selected_template.id,
            template_name=selected_template.name,
            template_path=Path(selected_template.file_path),
            tags=selected_template.tags,
            initial_data={k: str(v) for k, v in selected_record.input_data.items()},
            editing_record_id=selected_record.id,
            export_dir=self.export_dir,
            parent=self,
        )
        dialog.exec()
        self._reload_records()
