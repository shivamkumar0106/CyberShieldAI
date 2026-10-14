import sqlite3
import os
from flask import g
from config import Config

def get_db():
    """Get thread-local SQLite database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(Config.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_standalone_db():
    """Get a standalone database connection outside Flask request context (e.g. CLI, seed scripts)."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Create all 12 tables and necessary indexes."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
    os.makedirs(Config.SAMPLE_FOLDER, exist_ok=True)

    conn = get_standalone_db()
    cursor = conn.cursor()

    schema_sql = """
    -- 1. Users table
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'citizen',
        phone TEXT,
        badge_number TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 2. Cases table
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        incident_date TEXT NOT NULL,
        reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        loss_amount REAL DEFAULT 0.0,
        suspect_phone TEXT,
        suspect_email TEXT,
        suspect_upi TEXT,
        suspect_platform TEXT,
        status TEXT NOT NULL DEFAULT 'Submitted',
        priority TEXT NOT NULL DEFAULT 'Medium',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 3. Evidence Files table
    CREATE TABLE IF NOT EXISTS evidence_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        uploader_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        original_filename TEXT NOT NULL,
        stored_filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type TEXT NOT NULL,
        sha256_hash TEXT NOT NULL,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata_json TEXT,
        file_type TEXT NOT NULL,
        is_readonly INTEGER DEFAULT 1
    );

    -- 4. Analysis Runs table
    CREATE TABLE IF NOT EXISTS analysis_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        evidence_id INTEGER REFERENCES evidence_files(id) ON DELETE CASCADE,
        status TEXT NOT NULL DEFAULT 'completed',
        tool_versions TEXT,
        error_log TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    );

    -- 5. Extracted Text table
    CREATE TABLE IF NOT EXISTS extracted_text (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_id INTEGER NOT NULL REFERENCES evidence_files(id) ON DELETE CASCADE,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        extraction_method TEXT NOT NULL,
        source_page INTEGER DEFAULT 1,
        text_content TEXT NOT NULL,
        quality_score REAL DEFAULT 1.0,
        quality_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 6. Extracted Entities table
    CREATE TABLE IF NOT EXISTS entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        evidence_id INTEGER REFERENCES evidence_files(id) ON DELETE CASCADE,
        entity_type TEXT NOT NULL,
        entity_value TEXT NOT NULL,
        normalized_value TEXT NOT NULL,
        context TEXT,
        confidence REAL DEFAULT 0.95,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 7. Incident Events table
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        evidence_id INTEGER REFERENCES evidence_files(id) ON DELETE SET NULL,
        title TEXT NOT NULL,
        event_date TEXT NOT NULL,
        event_time TEXT,
        event_type TEXT DEFAULT 'INCIDENT_STEP',
        description TEXT NOT NULL,
        confidence REAL DEFAULT 0.9,
        verification_status TEXT DEFAULT 'Unverified',
        is_uncertain INTEGER DEFAULT 0,
        source_reference TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 8. Findings table (Cross-evidence consistency checks)
    CREATE TABLE IF NOT EXISTS findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        title TEXT NOT NULL,
        explanation TEXT NOT NULL,
        rule_name TEXT NOT NULL,
        matched_entities_json TEXT,
        conflicting_files_json TEXT,
        status TEXT NOT NULL DEFAULT 'Open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 9. Entity Evidence Links table
    CREATE TABLE IF NOT EXISTS entity_evidence_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
        evidence_id INTEGER NOT NULL REFERENCES evidence_files(id) ON DELETE CASCADE,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        mention_count INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(entity_id, evidence_id)
    );

    -- 10. Investigator Notes table
    CREATE TABLE IF NOT EXISTS investigator_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        investigator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        note_type TEXT DEFAULT 'Observation',
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 11. Audit Logs table
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER REFERENCES cases(id) ON DELETE SET NULL,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        action TEXT NOT NULL,
        target_type TEXT,
        target_id TEXT,
        details_json TEXT,
        ip_address TEXT DEFAULT '127.0.0.1',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 12. Reports table
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        report_number TEXT UNIQUE NOT NULL,
        file_path TEXT NOT NULL,
        generated_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        file_size INTEGER NOT NULL,
        sha256_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Performance Indexes
    CREATE INDEX IF NOT EXISTS idx_cases_user_id ON cases(user_id);
    CREATE INDEX IF NOT EXISTS idx_cases_case_id ON cases(case_id);
    CREATE INDEX IF NOT EXISTS idx_evidence_case_id ON evidence_files(case_id);
    CREATE INDEX IF NOT EXISTS idx_entities_case_id ON entities(case_id);
    CREATE INDEX IF NOT EXISTS idx_entities_norm_val ON entities(normalized_value);
    CREATE INDEX IF NOT EXISTS idx_events_case_id ON events(case_id);
    CREATE INDEX IF NOT EXISTS idx_findings_case_id ON findings(case_id);
    CREATE INDEX IF NOT EXISTS idx_audit_case_id ON audit_logs(case_id);
    """

    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("CyberShield SQLite Database initialized successfully with 12 core tables.")

if __name__ == '__main__':
    init_db()
