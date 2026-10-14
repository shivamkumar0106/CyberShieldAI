import os
import hashlib
import random
import string
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from config import Config
from modules.evidence import calculate_sha256, verify_file_integrity
from modules.audit import log_audit

def generate_pdf_report(case_id, investigator_id, db):
    """
    Generates an official-grade Digital Evidence Investigation Summary PDF using ReportLab.
    Includes case info, cryptographic hashes, cross-evidence findings, timeline, and limitations.
    """
    case = db.execute("""
        SELECT c.*, u.full_name as complainant_name, u.email as complainant_email, u.phone as complainant_phone
        FROM cases c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = ?
    """, (case_id,)).fetchone()
    
    if not case:
        return None, "Case not found"

    investigator = db.execute("SELECT * FROM users WHERE id = ?", (investigator_id,)).fetchone()
    investigator_name = investigator['full_name'] if investigator else "Authorized Investigator"
    badge_num = investigator['badge_number'] if investigator and investigator['badge_number'] else "CYBER-INV-01"

    evidence_files = db.execute(
        "SELECT * FROM evidence_files WHERE case_id = ? ORDER BY upload_time ASC", (case_id,)
    ).fetchall()

    findings = db.execute(
        "SELECT * FROM findings WHERE case_id = ? ORDER BY CASE severity WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END",
        (case_id,)
    ).fetchall()

    entities = db.execute("""
        SELECT e.*, ef.original_filename
        FROM entities e
        JOIN evidence_files ef ON e.evidence_id = ef.id
        WHERE e.case_id = ?
        ORDER BY e.entity_type, e.id
    """, (case_id,)).fetchall()

    events = db.execute(
        "SELECT * FROM events WHERE case_id = ? ORDER BY event_date ASC, event_time ASC", (case_id,)
    ).fetchall()

    notes = db.execute("""
        SELECT n.*, u.full_name as author_name
        FROM investigator_notes n
        JOIN users u ON n.investigator_id = u.id
        WHERE n.case_id = ?
        ORDER BY n.created_at ASC
    """, (case_id,)).fetchall()

    # Generate Unique Report Number
    timestamp_str = datetime.now().strftime('%Y%m%d-%H%M%S')
    rand_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    report_num = f"REP-{case['case_id']}-{timestamp_str}-{rand_suffix}"
    pdf_filename = f"{report_num}.pdf"
    os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
    pdf_path = os.path.join(Config.REPORT_FOLDER, pdf_filename)

    # Setup Document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    primary_color = colors.HexColor('#0f172a') # Slate 900
    brand_blue = colors.HexColor('#1e40af')    # Blue 800
    border_color = colors.HexColor('#cbd5e1')
    text_dark = colors.HexColor('#1e293b')
    subtext_color = colors.HexColor('#475569')

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=brand_blue,
        alignment=0,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=subtext_color,
        spaceAfter=12
    )

    heading2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=text_dark
    )

    bold_body_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#7f1d1d') # Red 900
    )

    story = []

    # Header Banner
    story.append(Paragraph("CYBERSHIELD AI — DIGITAL INVESTIGATION SUPPORT DOSSIER", title_style))
    story.append(Paragraph(
        f"<b>CONFIDENTIAL</b> | Case Reference: <b>{case['case_id']}</b> | Generated: {datetime.now().strftime('%d %b %Y, %H:%M:%S UTC')} | Reviewer: {investigator_name} ({badge_num})",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=brand_blue, spaceBefore=0, spaceAfter=10))

    # Case Overview Box
    case_info_data = [
        [
            Paragraph("<b>Case Reference:</b>", body_style), Paragraph(case['case_id'], bold_body_style),
            Paragraph("<b>Incident Category:</b>", body_style), Paragraph(case['category'], body_style)
        ],
        [
            Paragraph("<b>Complainant:</b>", body_style), Paragraph(f"{case['complainant_name']} ({case['complainant_email']})", body_style),
            Paragraph("<b>Claimed Loss:</b>", body_style), Paragraph(f"₹{case['loss_amount']:,.2f}", bold_body_style)
        ],
        [
            Paragraph("<b>Incident Date:</b>", body_style), Paragraph(case['incident_date'], body_style),
            Paragraph("<b>Current Status:</b>", body_style), Paragraph(case['status'].upper(), bold_body_style)
        ],
        [
            Paragraph("<b>Case Title:</b>", body_style),
            Paragraph(case['title'], body_style),
            Paragraph("<b>Reported On:</b>", body_style),
            Paragraph(str(case['reported_date']), body_style)
        ]
    ]
    t_case = Table(case_info_data, colWidths=[100, 170, 110, 160])
    t_case.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_case)
    story.append(Spacer(1, 10))

    # Complaint Narrative
    story.append(Paragraph("Incident Summary & Victim Statement", heading2_style))
    story.append(Paragraph(case['description'].replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 10))

    # SECTION 1: Digital Evidence Inventory & SHA-256 Hashes
    story.append(Paragraph("1. Digital Evidence Inventory & Cryptographic Custody", heading2_style))
    story.append(Paragraph("Every accepted file is preserved byte-for-byte in read-only custody. Cryptographic hashes ensure bit-level tamper detection.", subtitle_style))

    if evidence_files:
        ev_headers = ["File Name", "Type", "Size", "Upload Date", "SHA-256 Cryptographic Hash", "Integrity"]
        ev_rows = [[
            Paragraph(f"<b>{h}</b>", bold_body_style) for h in ev_headers
        ]]
        for ef in evidence_files:
            v_res = verify_file_integrity(ef['id'], db)
            integrity_str = "MATCHED (OK)" if v_res['matched'] else "MISMATCH (ALERT)"
            int_color = colors.HexColor('#166534') if v_res['matched'] else colors.HexColor('#b91c1c')

            ev_rows.append([
                Paragraph(ef['original_filename'], body_style),
                Paragraph(ef['file_type'].upper(), body_style),
                Paragraph(f"{ef['file_size'] // 1024} KB", body_style),
                Paragraph(str(ef['upload_time'])[:16], body_style),
                Paragraph(f"<font size=6>{ef['sha256_hash']}</font>", body_style),
                Paragraph(f"<font color='{int_color}'><b>{integrity_str}</b></font>", body_style)
            ])
        t_ev = Table(ev_rows, colWidths=[120, 45, 45, 80, 190, 60])
        t_ev.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_ev)
    else:
        story.append(Paragraph("<i>No evidence files recorded for this case.</i>", body_style))

    story.append(Spacer(1, 12))

    # SECTION 2: Automated Cross-Evidence Findings & Rule Results
    story.append(Paragraph("2. Automated Cross-Evidence Verification Findings", heading2_style))
    story.append(Paragraph("Deterministic rule checks comparing extracted entities, amounts, timestamps, and evidence gaps.", subtitle_style))

    if findings:
        f_headers = ["Severity", "Category", "Finding Title & Reason", "Status"]
        f_rows = [[
            Paragraph(f"<b>{h}</b>", bold_body_style) for h in f_headers
        ]]
        for f in findings:
            sev = f['severity']
            sev_color = colors.HexColor('#b91c1c') if sev == 'HIGH' else (colors.HexColor('#b45309') if sev == 'MEDIUM' else colors.HexColor('#15803d'))
            
            f_rows.append([
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", bold_body_style),
                Paragraph(f['category'].replace('_', ' '), body_style),
                Paragraph(f"<b>{f['title']}</b><br/>{f['explanation']}", body_style),
                Paragraph(f['status'], body_style)
            ])
        t_find = Table(f_rows, colWidths=[60, 95, 330, 55])
        t_find.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t_find)
    else:
        story.append(Paragraph("<i>No automated cross-evidence findings flagged.</i>", body_style))

    story.append(Spacer(1, 12))

    # SECTION 3: Extracted Technical Entities & Indicators
    story.append(Paragraph("3. Extracted Target Indicators & Forensic Identifiers", heading2_style))
    if entities:
        ent_headers = ["Type", "Identified Value", "Confidence", "Source Artifact"]
        ent_rows = [[
            Paragraph(f"<b>{h}</b>", bold_body_style) for h in ent_headers
        ]]
        # Take key structured identifiers
        key_ents = [e for e in entities if e['entity_type'] in ['UPI_ID', 'PHONE', 'TXN_REF', 'AMOUNT', 'EMAIL', 'URL_DOMAIN']]
        for ent in key_ents[:20]: # Cap to prevent giant PDF spillover
            ent_rows.append([
                Paragraph(f"<b>{ent['entity_type']}</b>", body_style),
                Paragraph(f"<code>{ent['entity_value']}</code>", body_style),
                Paragraph(f"{int((ent['confidence'] or 0.9)*100)}%", body_style),
                Paragraph(ent['original_filename'], body_style)
            ])
        t_ent = Table(ent_rows, colWidths=[90, 190, 70, 190])
        t_ent.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_ent)
    else:
        story.append(Paragraph("<i>No structured entities extracted.</i>", body_style))

    story.append(Spacer(1, 12))

    # SECTION 4: Reconstructed Chronological Timeline
    story.append(Paragraph("4. Reconstructed Incident Timeline", heading2_style))
    if events:
        ev_timeline_headers = ["Date & Time", "Event Description", "Verification Status", "Source Reference"]
        timeline_rows = [[
            Paragraph(f"<b>{h}</b>", bold_body_style) for h in ev_timeline_headers
        ]]
        for ev in events:
            time_display = f"{ev['event_date']} {ev['event_time'] or ''}".strip()
            timeline_rows.append([
                Paragraph(time_display, body_style),
                Paragraph(f"<b>{ev['title']}</b><br/>{ev['description']}", body_style),
                Paragraph(ev['verification_status'] or 'Unverified', body_style),
                Paragraph(ev['source_reference'] or 'Case File', body_style)
            ])
        t_time = Table(timeline_rows, colWidths=[90, 240, 100, 110])
        t_time.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t_time)
    else:
        story.append(Paragraph("<i>No timeline events established yet.</i>", body_style))

    story.append(Spacer(1, 12))

    # SECTION 5: Investigator Notes
    if notes:
        story.append(Paragraph("5. Investigator Notes & Observations", heading2_style))
        for n in notes:
            story.append(Paragraph(
                f"<b>[{n['note_type']}]</b> by {n['author_name']} on {str(n['created_at'])[:16]}:<br/>{n['content']}",
                body_style
            ))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 8))

    # SECTION 6: MANDATORY STATUTORY & SYSTEM BOUNDARIES DISCLAIMER
    story.append(Spacer(1, 10))
    disclaimer_box = [
        [
            Paragraph("<b>IMPORTANT NOTICE & STATUTORY FORENSIC DISCLAIMER:</b>", bold_body_style)
        ],
        [
            Paragraph(
                "CyberShield is an algorithmic investigation-support and evidence-organization system. "
                "It assists human investigators by extracting metadata, parsing optical characters, indexing cryptographic hashes, "
                "and executing deterministic consistency rules. "
                "<br/><br/>"
                "• <b>Advisory Scope:</b> This document does NOT replace an official police First Information Report (FIR), "
                "statutory certificate under Section 65B of the Indian Evidence Act (or equivalent electronic records admissibility statutes), "
                "or formal laboratory report from a government accredited Digital Forensics & Cybercrime Investigation Center. "
                "<br/>"
                "• <b>No Adjudication of Guilt:</b> Identifiers and entities extracted reflect textual appearances in the submitted files; "
                "they do not independently establish guilt, bad faith, or fraud without complete law enforcement verification. "
                "<br/>"
                "• <b>Evidence Custody:</b> Cryptographic SHA-256 digests prove non-alteration of the recorded files in CyberShield custody "
                "since intake time, but do not attest to the truthfulness or origin of the files prior to submission.",
                disclaimer_style
            )
        ]
    ]
    t_disc = Table(disclaimer_box, colWidths=[540])
    t_disc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')), # Red 50
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f87171')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_disc)

    # Build PDF
    doc.build(story)

    # Calculate report SHA-256
    pdf_size = os.path.getsize(pdf_path)
    pdf_hash = calculate_sha256(pdf_path)

    # Record in database
    cursor = db.execute("""
        INSERT INTO reports (case_id, report_number, file_path, generated_by, file_size, sha256_hash)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (case_id, report_num, pdf_path, investigator_id, pdf_size, pdf_hash))
    db.commit()
    report_id = cursor.lastrowid

    # (Case status preserved as designated in investigation workflow)

    log_audit(
        db, 'REPORT_GENERATED', case_id=case_id, user_id=investigator_id,
        target_type='REPORT', target_id=report_id,
        details={'report_number': report_num, 'sha256': pdf_hash, 'size_bytes': pdf_size}
    )

    return pdf_path, None
