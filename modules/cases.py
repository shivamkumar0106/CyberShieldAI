import os
import random
import string
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, jsonify, send_file, current_app
)
from database import get_db
from config import Config
from modules.auth import login_required, role_required
from modules.evidence import save_and_record_evidence, verify_file_integrity
from modules.extraction import process_evidence_file
from modules.verification import run_cross_evidence_verification
from modules.timeline import reconstruct_case_timeline
from modules.relationship_graph import generate_cytoscape_graph
from modules.reports import generate_pdf_report
from modules.audit import log_audit, get_case_audit_logs, get_all_audit_logs

cases_bp = Blueprint('cases', __name__)

def generate_case_id():
    """Generates a professional case tracking identifier like CS-2026-84912."""
    year = datetime.now().year
    digits = ''.join(random.choices(string.digits, k=5))
    return f"CS-{year}-{digits}"

# =========================================================================
# CITIZEN WORKFLOW
# =========================================================================

@cases_bp.route('/citizen/dashboard')
@login_required
def citizen_dashboard():
    db = get_db()
    user_id = session.get('user_id')
    user_cases = db.execute("""
        SELECT c.*, 
               (SELECT COUNT(*) FROM evidence_files WHERE case_id = c.id) as evidence_count,
               (SELECT COUNT(*) FROM findings WHERE case_id = c.id AND severity = 'HIGH') as alert_count
        FROM cases c
        WHERE c.user_id = ?
        ORDER BY c.reported_date DESC
    """, (user_id,)).fetchall()

    return render_template('citizen/my_cases.html', cases=user_cases)

@cases_bp.route('/citizen/report', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    db = get_db()
    user_id = session.get('user_id')

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        incident_date = request.form.get('incident_date', '').strip()
        loss_amount_raw = request.form.get('loss_amount', '0').strip()
        suspect_phone = request.form.get('suspect_phone', '').strip()
        suspect_email = request.form.get('suspect_email', '').strip()
        suspect_upi = request.form.get('suspect_upi', '').strip()
        suspect_platform = request.form.get('suspect_platform', '').strip()

        if not title or not category or not description or not incident_date:
            flash('Please complete all mandatory complaint fields (Title, Category, Date, and Description).', 'warning')
            return render_template('citizen/submit_complaint.html', categories=Config.CATEGORIES)

        try:
            loss_amount = float(loss_amount_raw.replace(',', '')) if loss_amount_raw else 0.0
        except ValueError:
            loss_amount = 0.0

        case_id_str = generate_case_id()
        cursor = db.execute("""
            INSERT INTO cases (
                case_id, user_id, title, category, description, incident_date,
                loss_amount, suspect_phone, suspect_email, suspect_upi, suspect_platform,
                status, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', 'Medium')
        """, (
            case_id_str, user_id, title, category, description, incident_date,
            loss_amount, suspect_phone, suspect_email, suspect_upi, suspect_platform
        ))
        db.commit()
        new_case_id = cursor.lastrowid

        log_audit(db, 'CASE_CREATED', case_id=new_case_id, user_id=user_id,
                  target_type='CASE', target_id=new_case_id,
                  details={'case_id': case_id_str, 'category': category, 'loss': loss_amount})

        # Process any uploaded evidence files
        uploaded_files = request.files.getlist('evidence_files')
        saved_evidence_ids = []
        errors = []

        for f in uploaded_files:
            if f and f.filename:
                ev_id, err = save_and_record_evidence(f, new_case_id, user_id, db)
                if err:
                    errors.append(f"{f.filename}: {err}")
                elif ev_id:
                    saved_evidence_ids.append(ev_id)
                    # Automatically initiate extraction pipeline for accepted evidence
                    process_evidence_file(ev_id, db)

        # Run cross-evidence verification and timeline reconstruction
        if saved_evidence_ids:
            run_cross_evidence_verification(new_case_id, db)
            reconstruct_case_timeline(new_case_id, db)

        if errors:
            flash(f"Complaint registered ({case_id_str}), but some files could not be accepted: {'; '.join(errors)}", 'warning')
        else:
            flash(f"Complaint successfully lodged! Your tracking reference is {case_id_str}.", 'success')

        return redirect(url_for('cases.track_case', case_ref=case_id_str))

    return render_template('citizen/submit_complaint.html', categories=Config.CATEGORIES)

@cases_bp.route('/track', methods=['GET', 'POST'])
def track_case():
    db = get_db()
    case_ref = request.args.get('case_ref', '').strip() or request.form.get('case_ref', '').strip()
    
    case = None
    timeline = []
    evidence_count = 0

    if case_ref:
        case = db.execute("SELECT * FROM cases WHERE case_id = ?", (case_ref,)).fetchone()
        if case:
            timeline = db.execute(
                "SELECT * FROM events WHERE case_id = ? ORDER BY event_date ASC, event_time ASC",
                (case['id'],)
            ).fetchall()
            evidence_count = db.execute(
                "SELECT COUNT(*) as cnt FROM evidence_files WHERE case_id = ?",
                (case['id'],)
            ).fetchone()['cnt']
        else:
            flash(f"No case found matching reference '{case_ref}'. Please verify the ID.", 'warning')

    return render_template('citizen/track_case.html', case=case, timeline=timeline, evidence_count=evidence_count, case_ref=case_ref)

# =========================================================================
# INVESTIGATOR WORKFLOW
# =========================================================================

@cases_bp.route('/investigator/dashboard')
@login_required
@role_required('investigator', 'admin')
def investigator_dashboard():
    db = get_db()
    
    # Aggregated Metrics
    total_cases = db.execute("SELECT COUNT(*) as cnt FROM cases").fetchone()['cnt']
    pending_cases = db.execute("SELECT COUNT(*) as cnt FROM cases WHERE status IN ('Submitted', 'Under Review')").fetchone()['cnt']
    verified_cases = db.execute("SELECT COUNT(*) as cnt FROM cases WHERE status IN ('Evidence Verified', 'Report Generated')").fetchone()['cnt']
    total_evidence = db.execute("SELECT COUNT(*) as cnt FROM evidence_files").fetchone()['cnt']
    high_findings = db.execute("SELECT COUNT(*) as cnt FROM findings WHERE severity = 'HIGH'").fetchone()['cnt']

    # Filter parameters
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    query = request.args.get('q', '').strip()

    sql = """
        SELECT c.*, u.full_name as complainant_name,
               (SELECT COUNT(*) FROM evidence_files WHERE case_id = c.id) as evidence_count,
               (SELECT COUNT(*) FROM findings WHERE case_id = c.id AND severity = 'HIGH') as high_flags,
               (SELECT COUNT(*) FROM findings WHERE case_id = c.id) as total_findings
        FROM cases c
        JOIN users u ON c.user_id = u.id
        WHERE 1=1
    """
    params = []

    if status_filter:
        sql += " AND c.status = ?"
        params.append(status_filter)
    if category_filter:
        sql += " AND c.category = ?"
        params.append(category_filter)
    if query:
        sql += " AND (c.case_id LIKE ? OR c.title LIKE ? OR c.description LIKE ? OR c.suspect_upi LIKE ? OR c.suspect_phone LIKE ?)"
        wildcard = f"%{query}%"
        params.extend([wildcard, wildcard, wildcard, wildcard, wildcard])

    sql += " ORDER BY c.reported_date DESC"
    all_cases = db.execute(sql, params).fetchall()

    return render_template(
        'investigator/dashboard.html',
        total_cases=total_cases,
        pending_cases=pending_cases,
        verified_cases=verified_cases,
        total_evidence=total_evidence,
        high_findings=high_findings,
        cases=all_cases,
        categories=Config.CATEGORIES,
        statuses=Config.STATUSES,
        current_status=status_filter,
        current_cat=category_filter,
        search_query=query
    )

@cases_bp.route('/investigator/case/<int:case_id>')
@login_required
@role_required('investigator', 'admin')
def case_workbench(case_id):
    db = get_db()
    case = db.execute("""
        SELECT c.*, u.full_name as complainant_name, u.email as complainant_email, u.phone as complainant_phone
        FROM cases c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = ?
    """, (case_id,)).fetchone()

    if not case:
        flash("Requested case not found.", "danger")
        return redirect(url_for('cases.investigator_dashboard'))

    evidence_files = db.execute("""
        SELECT ef.*,
               (SELECT COUNT(*) FROM entities WHERE evidence_id = ef.id) as entity_count,
               (SELECT quality_score FROM extracted_text WHERE evidence_id = ef.id LIMIT 1) as quality_score,
               (SELECT extraction_method FROM extracted_text WHERE evidence_id = ef.id LIMIT 1) as extraction_method,
               (SELECT quality_notes FROM extracted_text WHERE evidence_id = ef.id LIMIT 1) as quality_notes
        FROM evidence_files ef
        WHERE ef.case_id = ?
        ORDER BY ef.upload_time ASC
    """, (case_id,)).fetchall()

    extracted_texts = db.execute("""
        SELECT et.*, ef.original_filename
        FROM extracted_text et
        JOIN evidence_files ef ON et.evidence_id = ef.id
        WHERE et.case_id = ?
    """, (case_id,)).fetchall()

    entities = db.execute("""
        SELECT e.*, ef.original_filename
        FROM entities e
        JOIN evidence_files ef ON e.evidence_id = ef.id
        WHERE e.case_id = ?
        ORDER BY e.entity_type, e.id
    """, (case_id,)).fetchall()

    findings = db.execute("""
        SELECT * FROM findings WHERE case_id = ?
        ORDER BY CASE severity WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END
    """, (case_id,)).fetchall()

    timeline_events = db.execute("""
        SELECT * FROM events WHERE case_id = ?
        ORDER BY event_date ASC, event_time ASC
    """, (case_id,)).fetchall()

    notes = db.execute("""
        SELECT n.*, u.full_name as author_name, u.badge_number
        FROM investigator_notes n
        JOIN users u ON n.investigator_id = u.id
        WHERE n.case_id = ?
        ORDER BY n.created_at DESC
    """, (case_id,)).fetchall()

    reports = db.execute("""
        SELECT r.*, u.full_name as author_name
        FROM reports r
        JOIN users u ON r.generated_by = u.id
        WHERE r.case_id = ?
        ORDER BY r.created_at DESC
    """, (case_id,)).fetchall()

    audit_records = get_case_audit_logs(db, case_id)

    return render_template(
        'investigator/case_detail.html',
        case=case,
        evidence_files=evidence_files,
        extracted_texts=extracted_texts,
        entities=entities,
        findings=findings,
        timeline_events=timeline_events,
        notes=notes,
        reports=reports,
        audit_records=audit_records,
        statuses=Config.STATUSES
    )

# =========================================================================
# ACTIONS & API ENDPOINTS
# =========================================================================

@cases_bp.route('/investigator/case/<int:case_id>/upload-evidence', methods=['POST'])
@login_required
@role_required('investigator', 'admin')
def upload_additional_evidence(case_id):
    db = get_db()
    user_id = session.get('user_id')
    uploaded_files = request.files.getlist('evidence_files')
    count = 0
    errors = []

    for f in uploaded_files:
        if f and f.filename:
            ev_id, err = save_and_record_evidence(f, case_id, user_id, db)
            if err:
                errors.append(f"{f.filename}: {err}")
            elif ev_id:
                count += 1
                process_evidence_file(ev_id, db)

    if count > 0:
        run_cross_evidence_verification(case_id, db)
        reconstruct_case_timeline(case_id, db)
        flash(f"Successfully added and processed {count} evidence file(s).", "success")

    if errors:
        flash(f"Upload errors: {'; '.join(errors)}", "warning")

    return redirect(url_for('cases.case_workbench', case_id=case_id))

@cases_bp.route('/api/evidence/<int:evidence_id>/verify', methods=['GET', 'POST'])
@login_required
def api_verify_evidence(evidence_id):
    """Cryptographic SHA-256 live verification endpoint."""
    db = get_db()
    result = verify_file_integrity(evidence_id, db)
    return jsonify(result)

@cases_bp.route('/api/case/<int:case_id>/analyze', methods=['POST'])
@login_required
@role_required('investigator', 'admin')
def api_rerun_analysis(case_id):
    """Re-executes OCR, entity extraction, consistency verification, and timeline."""
    db = get_db()
    evidence_files = db.execute("SELECT id FROM evidence_files WHERE case_id = ?", (case_id,)).fetchall()
    
    for ef in evidence_files:
        process_evidence_file(ef['id'], db)

    findings = run_cross_evidence_verification(case_id, db)
    timeline = reconstruct_case_timeline(case_id, db)

    log_audit(
        db, 'ANALYSIS_RE_EXECUTED', case_id=case_id, user_id=session.get('user_id'),
        target_type='CASE', target_id=case_id,
        details={'files_processed': len(evidence_files), 'findings_count': len(findings)}
    )

    return jsonify({
        'status': 'success',
        'message': f"Analysis completed: {len(evidence_files)} files processed, {len(findings)} findings generated.",
        'findings_count': len(findings),
        'timeline_events_count': len(timeline)
    })

@cases_bp.route('/api/case/<int:case_id>/graph')
@login_required
def api_case_graph(case_id):
    """Returns Cytoscape.js nodes and edges JSON."""
    db = get_db()
    graph_data = generate_cytoscape_graph(case_id, db)
    return jsonify(graph_data)

@cases_bp.route('/investigator/case/<int:case_id>/note', methods=['POST'])
@login_required
@role_required('investigator', 'admin')
def add_investigator_note(case_id):
    db = get_db()
    user_id = session.get('user_id')
    content = request.form.get('content', '').strip()
    note_type = request.form.get('note_type', 'Observation')

    if content:
        db.execute("""
            INSERT INTO investigator_notes (case_id, investigator_id, note_type, content)
            VALUES (?, ?, ?, ?)
        """, (case_id, user_id, note_type, content))
        db.commit()
        log_audit(db, 'NOTE_ADDED', case_id=case_id, user_id=user_id,
                  target_type='CASE', target_id=case_id, details={'type': note_type})
        flash('Investigator note recorded successfully.', 'success')
    else:
        flash('Note content cannot be empty.', 'warning')

    return redirect(url_for('cases.case_workbench', case_id=case_id))

@cases_bp.route('/investigator/case/<int:case_id>/status', methods=['POST'])
@login_required
@role_required('investigator', 'admin')
def update_case_status(case_id):
    db = get_db()
    user_id = session.get('user_id')
    new_status = request.form.get('status')
    new_priority = request.form.get('priority')

    db.execute("""
        UPDATE cases SET status = ?, priority = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, new_priority, case_id))
    db.commit()

    log_audit(db, 'CASE_STATUS_UPDATED', case_id=case_id, user_id=user_id,
              target_type='CASE', target_id=case_id,
              details={'status': new_status, 'priority': new_priority})

    flash(f"Case updated to status '{new_status}' with '{new_priority}' priority.", 'info')
    return redirect(url_for('cases.case_workbench', case_id=case_id))

@cases_bp.route('/investigator/case/<int:case_id>/generate-report', methods=['POST', 'GET'])
@login_required
@role_required('investigator', 'admin')
def trigger_report_generation(case_id):
    db = get_db()
    user_id = session.get('user_id')
    pdf_path, err = generate_pdf_report(case_id, user_id, db)
    if err:
        flash(f"Error generating report: {err}", "danger")
        return redirect(url_for('cases.case_workbench', case_id=case_id))

    flash("Investigation PDF dossier generated successfully.", "success")
    return redirect(url_for('cases.download_report_file', case_id=case_id))

@cases_bp.route('/investigator/case/<int:case_id>/report/download')
def download_report_file(case_id):
    db = get_db()
    report = db.execute(
        "SELECT * FROM reports WHERE case_id = ? ORDER BY created_at DESC LIMIT 1",
        (case_id,)
    ).fetchone()

    if not report or not os.path.exists(report['file_path']):
        user_id = session.get('user_id', 1)
        pdf_path, err = generate_pdf_report(case_id, user_id, db)
        if err or not pdf_path or not os.path.exists(pdf_path):
            flash("Unable to generate PDF report for this case.", "warning")
            return redirect(f"/pages/case-details.html?id={case_id}")
        report = db.execute(
            "SELECT * FROM reports WHERE case_id = ? ORDER BY created_at DESC LIMIT 1",
            (case_id,)
        ).fetchone()

    return send_file(
        report['file_path'],
        as_attachment=True,
        download_name=f"{report['report_number']}.pdf",
        mimetype='application/pdf'
    )

@cases_bp.route('/evidence/<int:evidence_id>/view')
@login_required
def view_evidence_file(evidence_id):
    """Safely serves raw evidence file in browser (read-only)."""
    db = get_db()
    ef = db.execute("SELECT * FROM evidence_files WHERE id = ?", (evidence_id,)).fetchone()
    if not ef or not os.path.exists(ef['file_path']):
        flash("Evidence file not found on disk.", "danger")
        return redirect(url_for('cases.investigator_dashboard'))

    return send_file(ef['file_path'], mimetype=ef['mime_type'])

@cases_bp.route('/investigator/audit-logs')
@login_required
@role_required('investigator', 'admin')
def audit_logs_page():
    db = get_db()
    logs = get_all_audit_logs(db, limit=200)
    return render_template('investigator/audit_logs.html', logs=logs)
