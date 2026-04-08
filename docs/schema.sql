CREATE TABLE Templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE Records (
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

CREATE TABLE Profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_key TEXT NOT NULL UNIQUE,
    profile_data_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
