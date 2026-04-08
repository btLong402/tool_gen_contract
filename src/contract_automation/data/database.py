from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from contract_automation.models import RecordItem, TemplateItem


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS Templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS Records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                input_data_json TEXT NOT NULL,
                output_docx_path TEXT,
                output_pdf_path TEXT,
                partner_key TEXT,
                is_draft INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (template_id) REFERENCES Templates(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_key TEXT NOT NULL UNIQUE,
                profile_data_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
            """
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def add_template(self, name: str, file_path: str, tags: list[str]) -> int:
        cursor = self.conn.execute(
            "INSERT INTO Templates(name, file_path, tags_json) VALUES (?, ?, ?)",
            (name, file_path, json.dumps(tags)),
        )
        self.conn.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to retrieve inserted template id")
        return int(cursor.lastrowid)

    def list_templates(self) -> list[TemplateItem]:
        rows = self.conn.execute(
            "SELECT id, name, file_path, tags_json, created_at FROM Templates ORDER BY id DESC"
        ).fetchall()
        items: list[TemplateItem] = []
        for row in rows:
            items.append(
                TemplateItem(
                    id=row["id"],
                    name=row["name"],
                    file_path=row["file_path"],
                    tags=json.loads(row["tags_json"]),
                    created_at=row["created_at"],
                )
            )
        return items

    def delete_template(self, template_id: int) -> None:
        self.conn.execute("DELETE FROM Templates WHERE id = ?", (template_id,))
        self.conn.commit()

    def create_record(
        self,
        template_id: int,
        input_data: dict[str, Any],
        output_docx_path: str | None,
        output_pdf_path: str | None,
        partner_key: str | None,
        is_draft: bool,
    ) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO Records(
                template_id,
                input_data_json,
                output_docx_path,
                output_pdf_path,
                partner_key,
                is_draft
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                template_id,
                json.dumps(input_data, ensure_ascii=False),
                output_docx_path,
                output_pdf_path,
                partner_key,
                1 if is_draft else 0,
            ),
        )
        self.conn.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to retrieve inserted record id")
        return int(cursor.lastrowid)

    def list_records_for_template(self, template_id: int) -> list[RecordItem]:
        rows = self.conn.execute(
            """
            SELECT
                id,
                template_id,
                input_data_json,
                output_docx_path,
                output_pdf_path,
                partner_key,
                is_draft,
                created_at
            FROM Records
            WHERE template_id = ?
            ORDER BY id DESC
            """,
            (template_id,),
        ).fetchall()

        result: list[RecordItem] = []
        for row in rows:
            result.append(
                RecordItem(
                    id=row["id"],
                    template_id=row["template_id"],
                    input_data=json.loads(row["input_data_json"]),
                    output_docx_path=row["output_docx_path"],
                    output_pdf_path=row["output_pdf_path"],
                    partner_key=row["partner_key"],
                    is_draft=bool(row["is_draft"]),
                    created_at=row["created_at"],
                )
            )
        return result

    def get_record_by_id(self, record_id: int) -> RecordItem | None:
        row = self.conn.execute(
            """
            SELECT
                id,
                template_id,
                input_data_json,
                output_docx_path,
                output_pdf_path,
                partner_key,
                is_draft,
                created_at
            FROM Records
            WHERE id = ?
            """,
            (record_id,),
        ).fetchone()
        if not row:
            return None

        return RecordItem(
            id=row["id"],
            template_id=row["template_id"],
            input_data=json.loads(row["input_data_json"]),
            output_docx_path=row["output_docx_path"],
            output_pdf_path=row["output_pdf_path"],
            partner_key=row["partner_key"],
            is_draft=bool(row["is_draft"]),
            created_at=row["created_at"],
        )

    def update_record(
        self,
        record_id: int,
        input_data: dict[str, Any],
        output_docx_path: str | None,
        output_pdf_path: str | None,
        partner_key: str | None,
        is_draft: bool,
    ) -> None:
        self.conn.execute(
            """
            UPDATE Records
            SET
                input_data_json = ?,
                output_docx_path = ?,
                output_pdf_path = ?,
                partner_key = ?,
                is_draft = ?,
                created_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (
                json.dumps(input_data, ensure_ascii=False),
                output_docx_path,
                output_pdf_path,
                partner_key,
                1 if is_draft else 0,
                record_id,
            ),
        )
        self.conn.commit()

    def upsert_profile(self, partner_key: str, profile_data: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO Profiles(partner_key, profile_data_json)
            VALUES (?, ?)
            ON CONFLICT(partner_key)
            DO UPDATE SET
                profile_data_json = excluded.profile_data_json,
                updated_at = datetime('now', 'localtime')
            """,
            (partner_key, json.dumps(profile_data, ensure_ascii=False)),
        )
        self.conn.commit()

    def get_profile(self, partner_key: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT profile_data_json FROM Profiles WHERE partner_key = ?",
            (partner_key,),
        ).fetchone()
        if not row:
            return None
        return json.loads(row["profile_data_json"])
