import json
from flask import request

def log_audit(db, action, case_id=None, user_id=None, target_type=None, target_id=None, details=None, ip_address=None):
    """
    Record an immutable audit log entry for tamper-evidence and chain of custody tracking.
    """
    if details is not None and not isinstance(details, str):
        try:
            details = json.dumps(details, default=str)
        except Exception:
            details = str(details)

    if ip_address is None:
        try:
            ip_address = request.remote_addr if request else '127.0.0.1'
        except RuntimeError:
            ip_address = '127.0.0.1'

    db.execute("""
        INSERT INTO audit_logs (case_id, user_id, action, target_type, target_id, details_json, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (case_id, user_id, action, target_type, str(target_id) if target_id is not None else None, details, ip_address))
    db.commit()

def get_case_audit_logs(db, case_id):
    """Retrieve audit logs for a specific case with user details."""
    return db.execute("""
        SELECT a.*, u.full_name as user_name, u.role as user_role
        FROM audit_logs a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE a.case_id = ?
        ORDER BY a.timestamp DESC
    """, (case_id,)).fetchall()

def get_all_audit_logs(db, limit=100):
    """Retrieve system-wide audit logs."""
    return db.execute("""
        SELECT a.*, u.full_name as user_name, u.role as user_role, c.case_id as case_ref
        FROM audit_logs a
        LEFT JOIN users u ON a.user_id = u.id
        LEFT JOIN cases c ON a.case_id = c.id
        ORDER BY a.timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()
