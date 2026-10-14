import json
from datetime import datetime
from modules.evidence import verify_file_integrity

def run_cross_evidence_verification(case_id, db):
    """
    Executes explainable rule-based cross-evidence consistency and correlation checks.
    Clears previous findings and inserts updated findings with explicit reasons.
    """
    case = db.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    if not case:
        return []

    evidence_files = db.execute(
        "SELECT * FROM evidence_files WHERE case_id = ?", (case_id,)
    ).fetchall()

    entities = db.execute(
        "SELECT e.*, ef.original_filename FROM entities e "
        "JOIN evidence_files ef ON e.evidence_id = ef.id "
        "WHERE e.case_id = ?", (case_id,)
    ).fetchall()

    # Clear prior findings for this case
    db.execute("DELETE FROM findings WHERE case_id = ?", (case_id,))

    findings = []

    # ---------------------------------------------------------
    # RULE 1: Tamper-Evident Integrity Check Across All Evidence
    # ---------------------------------------------------------
    tampered_files = []
    for ef in evidence_files:
        res = verify_file_integrity(ef['id'], db)
        if not res['matched']:
            tampered_files.append(ef['original_filename'])

    if tampered_files:
        f = {
            'case_id': case_id,
            'category': 'INTEGRITY_ALERT',
            'severity': 'HIGH',
            'title': 'Evidence Integrity Tamper Warning',
            'explanation': f"The following evidence files failed cryptographic SHA-256 verification: {', '.join(tampered_files)}. Their bytes differ from the original upload state.",
            'rule_name': 'RULE_SHA256_HASH_VERIFY',
            'matched_entities_json': json.dumps([]),
            'conflicting_files_json': json.dumps(tampered_files),
            'status': 'Open'
        }
        findings.append(f)
    else:
        if evidence_files:
            f = {
                'case_id': case_id,
                'category': 'INTEGRITY_CHECK',
                'severity': 'INFO',
                'title': 'Cryptographic Integrity Confirmed',
                'explanation': f"All {len(evidence_files)} uploaded evidence files match their original SHA-256 cryptographic hashes exactly. No post-upload file alterations detected.",
                'rule_name': 'RULE_SHA256_HASH_VERIFY',
                'matched_entities_json': json.dumps([]),
                'conflicting_files_json': json.dumps([]),
                'status': 'Reviewed'
            }
            findings.append(f)

    # ---------------------------------------------------------
    # RULE 2: Cross-File Entity Correlation (Matching Identifiers)
    # ---------------------------------------------------------
    entity_map = {}
    for ent in entities:
        key = (ent['entity_type'], ent['normalized_value'])
        if key not in entity_map:
            entity_map[key] = []
        entity_map[key].append({
            'evidence_id': ent['evidence_id'],
            'filename': ent['original_filename'],
            'val': ent['entity_value']
        })

    for (etype, norm_val), occurrences in entity_map.items():
        unique_files = list(set([o['filename'] for o in occurrences]))
        if len(unique_files) > 1 and etype in ['UPI_ID', 'PHONE', 'TXN_REF', 'EMAIL']:
            f = {
                'case_id': case_id,
                'category': 'MATCH_CONFIRMED',
                'severity': 'LOW',
                'title': f'Cross-Corroborated {etype.replace("_", " ")} Identified',
                'explanation': (
                    f"The identifier '{norm_val}' was detected across {len(unique_files)} separate evidence files "
                    f"({', '.join(unique_files)}). This establishes a strong documentary link in the submitted records."
                ),
                'rule_name': 'RULE_CROSS_FILE_MATCH',
                'matched_entities_json': json.dumps([norm_val]),
                'conflicting_files_json': json.dumps(unique_files),
                'status': 'Open'
            }
            findings.append(f)

    # Corroborate with suspect information submitted in the complaint form
    suspect_fields = [
        ('suspect_upi', 'UPI_ID', case['suspect_upi']),
        ('suspect_phone', 'PHONE', case['suspect_phone']),
        ('suspect_email', 'EMAIL', case['suspect_email'])
    ]
    for field_name, etype, suspect_val in suspect_fields:
        if suspect_val:
            cleaned_suspect = suspect_val.strip().lower()
            matching_files = set()
            for ent in entities:
                if ent['entity_type'] == etype and (cleaned_suspect in ent['normalized_value'].lower() or ent['normalized_value'].lower() in cleaned_suspect):
                    matching_files.add(ent['original_filename'])
            if matching_files:
                f = {
                    'case_id': case_id,
                    'category': 'MATCH_CONFIRMED',
                    'severity': 'LOW',
                    'title': f'Complaint Suspect {etype.replace("_", " ")} Verified in Evidence',
                    'explanation': (
                        f"The suspect {etype.replace('_', ' ')} '{suspect_val}' claimed by the victim was directly verified "
                        f"in uploaded evidence file(s): {', '.join(matching_files)}."
                    ),
                    'rule_name': 'RULE_COMPLAINT_EVIDENCE_CORRELATION',
                    'matched_entities_json': json.dumps([suspect_val]),
                    'conflicting_files_json': json.dumps(list(matching_files)),
                    'status': 'Reviewed'
                }
                findings.append(f)

    # ---------------------------------------------------------
    # RULE 3: Financial Loss vs Extracted Receipts Check
    # ---------------------------------------------------------
    claimed_loss = float(case['loss_amount'] or 0.0)
    extracted_amounts = []
    for ent in entities:
        if ent['entity_type'] == 'AMOUNT':
            try:
                amt = float(ent['normalized_value'])
                extracted_amounts.append(amt)
            except ValueError:
                pass

    if claimed_loss > 0 and extracted_amounts:
        max_extracted = max(extracted_amounts)
        sum_extracted = sum(set(extracted_amounts)) # Unique amounts
        
        # Check if claimed loss matches exactly any extracted receipt amount
        matched_exact = any(abs(claimed_loss - amt) < 1.0 for amt in extracted_amounts)
        
        if matched_exact:
            f = {
                'case_id': case_id,
                'category': 'MATCH_CONFIRMED',
                'severity': 'LOW',
                'title': 'Claimed Loss Corroborated by Evidence Amount',
                'explanation': f"The reported monetary loss of ₹{claimed_loss:,.2f} corresponds directly to an amount extracted from uploaded transaction evidence.",
                'rule_name': 'RULE_AMOUNT_CORROBORATION',
                'matched_entities_json': json.dumps([f"₹{claimed_loss:,.2f}"]),
                'conflicting_files_json': json.dumps([]),
                'status': 'Reviewed'
            }
            findings.append(f)
        elif abs(claimed_loss - sum_extracted) < 1.0:
            f = {
                'case_id': case_id,
                'category': 'MATCH_CONFIRMED',
                'severity': 'LOW',
                'title': 'Aggregated Multi-Transaction Loss Matches Claim',
                'explanation': f"The claimed financial loss of ₹{claimed_loss:,.2f} exactly matches the cumulative sum of multiple separate transaction amounts found across the evidence files.",
                'rule_name': 'RULE_CUMULATIVE_AMOUNT_MATCH',
                'matched_entities_json': json.dumps([f"₹{claimed_loss:,.2f}"]),
                'conflicting_files_json': json.dumps([]),
                'status': 'Reviewed'
            }
            findings.append(f)
        else:
            f = {
                'case_id': case_id,
                'category': 'DISCREPANCY_FLAG',
                'severity': 'MEDIUM',
                'title': 'Discrepancy Between Claimed Loss and Documented Receipts',
                'explanation': (
                    f"The complaint reports a financial loss of ₹{claimed_loss:,.2f}, but the closest extracted receipt amounts "
                    f"are ₹{max_extracted:,.2f} (highest single) or ₹{sum_extracted:,.2f} (total observed). "
                    f"Investigator should review whether additional transaction receipts or bank statements remain unsubmitted."
                ),
                'rule_name': 'RULE_AMOUNT_DISCREPANCY_CHECK',
                'matched_entities_json': json.dumps([f"₹{claimed_loss}", f"₹{max_extracted}"]),
                'conflicting_files_json': json.dumps([]),
                'status': 'Open'
            }
            findings.append(f)

    # ---------------------------------------------------------
    # RULE 4: Category-Specific Evidence Completeness (Evidence Gap)
    # ---------------------------------------------------------
    category = case['category']
    txn_refs = [e for e in entities if e['entity_type'] == 'TXN_REF']
    upi_ids = [e for e in entities if e['entity_type'] == 'UPI_ID']
    domains = [e for e in entities if e['entity_type'] == 'URL_DOMAIN']

    if 'Payment' in category or 'UPI' in category:
        if not txn_refs and not upi_ids:
            f = {
                'case_id': case_id,
                'category': 'EVIDENCE_GAP',
                'severity': 'HIGH',
                'title': 'Missing Core Banking / UPI Identifiers',
                'explanation': (
                    "In an online payment or UPI fraud complaint, a 12-digit UTR number or UPI transaction reference is essential. "
                    "Neither a UTR nor a recipient UPI address could be definitively extracted from current evidence files. "
                    "Action recommended: Request victim upload official bank account debit statement or payment app detailed receipt."
                ),
                'rule_name': 'RULE_PAYMENT_CORE_EVIDENCE_GAP',
                'matched_entities_json': json.dumps([]),
                'conflicting_files_json': json.dumps([]),
                'status': 'Open'
            }
            findings.append(f)

    if 'Phishing' in category:
        if not domains and not any(e['entity_type'] == 'EMAIL' for e in entities):
            f = {
                'case_id': case_id,
                'category': 'EVIDENCE_GAP',
                'severity': 'MEDIUM',
                'title': 'Missing Phishing URL or Email Header Evidence',
                'explanation': (
                    "Phishing investigation requires either the deceptive link/domain or email header artifacts. "
                    "No web domain or email addresses were identified in the current submissions."
                ),
                'rule_name': 'RULE_PHISHING_DOMAIN_GAP',
                'matched_entities_json': json.dumps([]),
                'conflicting_files_json': json.dumps([]),
                'status': 'Open'
            }
            findings.append(f)

    # Save all findings to database
    for f in findings:
        db.execute("""
            INSERT INTO findings (
                case_id, category, severity, title, explanation,
                rule_name, matched_entities_json, conflicting_files_json, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f['case_id'], f['category'], f['severity'], f['title'],
            f['explanation'], f['rule_name'], f['matched_entities_json'],
            f['conflicting_files_json'], f['status']
        ))

    db.commit()
    return findings
