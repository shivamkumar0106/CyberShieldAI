import json
import re
from datetime import datetime

def parse_flexible_date(date_str):
    """
    Attempts to parse multiple date formats commonly found in cyber evidence.
    Returns (iso_date_string, is_uncertain).
    """
    if not date_str:
        return None, True

    date_str = str(date_str).strip()
    
    # Try ISO YYYY-MM-DD
    iso_match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', date_str)
    if iso_match:
        try:
            y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
            dt = datetime(y, m, d)
            return dt.strftime('%Y-%m-%d'), False
        except ValueError:
            pass

    # Try DD/MM/YYYY or DD-MM-YYYY
    dmy_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', date_str)
    if dmy_match:
        try:
            d, m, y = int(dmy_match.group(1)), int(dmy_match.group(2)), int(dmy_match.group(3))
            dt = datetime(y, m, d)
            return dt.strftime('%Y-%m-%d'), False
        except ValueError:
            pass

    # Try EXIF format YYYY:MM:DD HH:MM:SS
    exif_match = re.search(r'(\d{4}):(\d{2}):(\d{2})\s*(\d{2}):(\d{2}):(\d{2})?', date_str)
    if exif_match:
        try:
            y, m, d = int(exif_match.group(1)), int(exif_match.group(2)), int(exif_match.group(3))
            dt = datetime(y, m, d)
            return dt.strftime('%Y-%m-%d'), False
        except ValueError:
            pass

    return None, True

def reconstruct_case_timeline(case_id, db):
    """
    Reconstructs the chronological incident timeline from:
    1. Incident date declared in complaint statement
    2. Extracted dates from evidence text & OCR
    3. File metadata creation timestamps (EXIF / PDF)
    4. Evidence upload timestamps
    """
    case = db.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    if not case:
        return []

    evidence_files = db.execute("SELECT * FROM evidence_files WHERE case_id = ?", (case_id,)).fetchall()
    extracted_dates = db.execute("""
        SELECT e.*, ef.original_filename 
        FROM entities e
        JOIN evidence_files ef ON e.evidence_id = ef.id
        WHERE e.case_id = ? AND e.entity_type = 'DATE'
    """, (case_id,)).fetchall()

    # Clear prior auto-generated events for clean reconstruction
    db.execute("DELETE FROM events WHERE case_id = ?", (case_id,))

    timeline_events = []

    # 1. Complainant's Claimed Incident Date
    incident_iso, _ = parse_flexible_date(case['incident_date'])
    if not incident_iso:
        incident_iso = datetime.now().strftime('%Y-%m-%d')
        is_uncertain = 1
    else:
        is_uncertain = 0

    timeline_events.append({
        'case_id': case_id,
        'evidence_id': None,
        'title': 'Reported Incident Initiation',
        'event_date': incident_iso,
        'event_time': '00:00:00',
        'event_type': 'INITIAL_CONTACT',
        'description': f"Complainant reported occurrence of {case['category']}. Statement: {case['title']}",
        'confidence': 0.95,
        'verification_status': 'Complainant Statement',
        'is_uncertain': is_uncertain,
        'source_reference': f"Complaint Form ({case['case_id']})"
    })

    # 2. File Metadata Timestamps (EXIF / Document Creation)
    for ef in evidence_files:
        if ef['metadata_json']:
            try:
                meta = json.loads(ef['metadata_json'])
                created_date_raw = meta.get('creation_date') or (meta.get('exif', {}).get('DateTimeOriginal') if isinstance(meta.get('exif'), dict) else None)
                if created_date_raw:
                    file_date, uncert = parse_flexible_date(created_date_raw)
                    if file_date:
                        timeline_events.append({
                            'case_id': case_id,
                            'evidence_id': ef['id'],
                            'title': f"Evidence Captured / Artifact Created: {ef['original_filename']}",
                            'event_date': file_date,
                            'event_time': '12:00:00',
                            'event_type': 'ARTIFACT_CAPTURE',
                            'description': f"Embedded file metadata indicates file '{ef['original_filename']}' was created on {created_date_raw}.",
                            'confidence': 0.88,
                            'verification_status': 'Verified via File Metadata',
                            'is_uncertain': 0,
                            'source_reference': ef['original_filename']
                        })
            except Exception:
                pass

    # 3. Extracted Dates from OCR / Receipt Text
    for ent in extracted_dates:
        parsed_d, is_uncert = parse_flexible_date(ent['entity_value'])
        if parsed_d:
            context_snippet = ent['context'] or ''
            # Determine if this corresponds to a transaction or chat message
            event_type = 'DOCUMENTED_ACTIVITY'
            title = f"Documented Date in {ent['original_filename']}"
            if any(term in context_snippet.lower() for term in ['paid', 'debit', 'txn', 'utr', 'transfer', 'amount', 'rs', 'inr', 'successful']):
                event_type = 'TRANSACTION_EVENT'
                title = f"Transaction Occurrence: {ent['original_filename']}"
            elif any(term in context_snippet.lower() for term in ['message', 'sent', 'chat', 'telegram', 'whatsapp']):
                event_type = 'COMMUNICATION_EVENT'
                title = f"Communication Timestamp: {ent['original_filename']}"

            timeline_events.append({
                'case_id': case_id,
                'evidence_id': ent['evidence_id'],
                'title': title,
                'event_date': parsed_d,
                'event_time': '10:00:00',
                'event_type': event_type,
                'description': f"Extracted timestamp reference '{ent['entity_value']}'. Context: \"{context_snippet}\"",
                'confidence': float(ent['confidence'] or 0.85),
                'verification_status': 'Extracted from Evidence Text',
                'is_uncertain': 1 if is_uncert else 0,
                'source_reference': ent['original_filename']
            })

    # 4. Complaint Submission Event
    reported_str = case['reported_date']
    reported_iso, _ = parse_flexible_date(reported_str)
    if not reported_iso:
        reported_iso = datetime.now().strftime('%Y-%m-%d')

    timeline_events.append({
        'case_id': case_id,
        'evidence_id': None,
        'title': 'Formal CyberShield Complaint Registration',
        'event_date': reported_iso,
        'event_time': '23:59:59',
        'event_type': 'COMPLAINT_REGISTERED',
        'description': f"Complaint {case['case_id']} formally received and cryptographic evidence custody initiated.",
        'confidence': 1.0,
        'verification_status': 'System Recorded',
        'is_uncertain': 0,
        'source_reference': 'CyberShield Intake Log'
    })

    # Deduplicate events with same date, title, and source
    unique_events = []
    seen = set()
    for ev in timeline_events:
        key = (ev['event_date'], ev['title'], ev['source_reference'])
        if key not in seen:
            seen.add(key)
            unique_events.append(ev)

    # Sort strictly by event_date ascending, then time
    unique_events.sort(key=lambda x: (x['event_date'], x.get('event_time', '00:00:00')))

    # Commit to database
    for ev in unique_events:
        db.execute("""
            INSERT INTO events (
                case_id, evidence_id, title, event_date, event_time,
                event_type, description, confidence, verification_status,
                is_uncertain, source_reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ev['case_id'], ev['evidence_id'], ev['title'], ev['event_date'],
            ev['event_time'], ev['event_type'], ev['description'],
            ev['confidence'], ev['verification_status'], ev['is_uncertain'],
            ev['source_reference']
        ))

    db.commit()
    return unique_events
