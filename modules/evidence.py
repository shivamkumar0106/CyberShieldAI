import os
import hashlib
import mimetypes
from pathlib import Path
from werkzeug.utils import secure_filename
from config import Config
from modules.audit import log_audit

def allowed_file(filename):
    """Check if file extension is among allowed formats."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def calculate_sha256(filepath_or_bytes):
    """Compute SHA-256 cryptographic digest."""
    sha256 = hashlib.sha256()
    if isinstance(filepath_or_bytes, (bytes, bytearray)):
        sha256.update(filepath_or_bytes)
        return sha256.hexdigest()
    
    with open(filepath_or_bytes, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def detect_file_type(filename):
    """Classify file into image, pdf, or text."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in ['jpg', 'jpeg', 'png']:
        return 'image'
    elif ext == 'pdf':
        return 'pdf'
    elif ext == 'txt':
        return 'text'
    return 'unknown'

def save_and_record_evidence(file_obj, case_id, uploader_id, db):
    """
    Safely stores an uploaded evidence file:
    1. Reads bytes
    2. Computes SHA-256 immediately
    3. Saves file with a unique secure timestamped name
    4. Sets write permissions to read-only
    5. Inserts record into database
    6. Logs audit event
    """
    if not file_obj or file_obj.filename == '':
        return None, "No file provided"

    orig_name = secure_filename(file_obj.filename)
    if not orig_name or not allowed_file(orig_name):
        return None, f"File format not permitted. Allowed: {', '.join(Config.ALLOWED_EXTENSIONS)}"

    file_bytes = file_obj.read()
    file_size = len(file_bytes)

    if file_size > Config.MAX_CONTENT_LENGTH:
        return None, f"File exceeds maximum allowed size ({Config.MAX_CONTENT_LENGTH // (1024*1024)} MB)"

    # Compute immediate cryptographic hash before writing
    file_hash = calculate_sha256(file_bytes)

    # Generate safe unique filename
    ext = orig_name.rsplit('.', 1)[1].lower()
    short_hash = file_hash[:10]
    stored_name = f"CASE_{case_id}_{short_hash}_{orig_name}"
    
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    destination_path = os.path.join(Config.UPLOAD_FOLDER, stored_name)

    # Save byte-for-byte to disk
    with open(destination_path, 'wb') as dest:
        dest.write(file_bytes)

    # Ensure read-only file permissions to preserve integrity
    try:
        import stat
        os.chmod(destination_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    except Exception:
        pass

    mime_type, _ = mimetypes.guess_type(orig_name)
    if not mime_type:
        mime_type = 'application/octet-stream'

    file_type = detect_file_type(orig_name)

    cursor = db.execute("""
        INSERT INTO evidence_files (
            case_id, uploader_id, original_filename, stored_filename,
            file_path, file_size, mime_type, sha256_hash, file_type, is_readonly
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        case_id, uploader_id, orig_name, stored_name,
        destination_path, file_size, mime_type, file_hash, file_type
    ))
    db.commit()
    evidence_id = cursor.lastrowid

    log_audit(
        db, 'EVIDENCE_UPLOADED', case_id=case_id, user_id=uploader_id,
        target_type='EVIDENCE', target_id=evidence_id,
        details={'filename': orig_name, 'sha256': file_hash, 'size': file_size}
    )

    return evidence_id, None

def verify_file_integrity(evidence_id, db):
    """
    Recalculates file hash on disk and compares against recorded hash in database.
    Detects any file alteration, truncation, or bit rot.
    """
    row = db.execute("SELECT * FROM evidence_files WHERE id = ?", (evidence_id,)).fetchone()
    if not row:
        return {'status': 'error', 'message': 'Evidence record not found'}

    file_path = row['file_path']
    recorded_hash = row['sha256_hash']

    if not os.path.exists(file_path):
        return {
            'status': 'missing',
            'matched': False,
            'message': 'File missing from storage disk',
            'recorded_hash': recorded_hash,
            'current_hash': None
        }

    current_hash = calculate_sha256(file_path)
    matched = (current_hash.lower() == recorded_hash.lower())

    log_audit(
        db, 'INTEGRITY_VERIFIED', case_id=row['case_id'],
        target_type='EVIDENCE', target_id=evidence_id,
        details={'match': matched, 'current_hash': current_hash, 'expected_hash': recorded_hash}
    )

    return {
        'status': 'verified' if matched else 'tampered',
        'matched': matched,
        'filename': row['original_filename'],
        'recorded_hash': recorded_hash,
        'current_hash': current_hash,
        'message': 'Cryptographic hash intact. Original bytes unchanged.' if matched else 'Integrity warning: File hash mismatch detected!'
    }
