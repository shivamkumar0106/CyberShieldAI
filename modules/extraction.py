import os
import re
import json
import pymupdf as fitz
from PIL import Image, ExifTags
import pytesseract
import spacy
from database import get_db

# Try loading spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Configure Tesseract path if found in common Windows locations
COMMON_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
]
for p in COMMON_TESSERACT_PATHS:
    if os.path.exists(p):
        pytesseract.pytesseract.tesseract_cmd = p
        break

# Regex Patterns tailored for cybercrime evidence
PATTERNS = {
    'UPI_ID': re.compile(r'\b[a-zA-Z0-9.\-_]{2,64}@(?!gmail|yahoo|outlook|hotmail|icloud)[a-zA-Z]{2,32}\b', re.IGNORECASE),
    'EMAIL': re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b', re.IGNORECASE),
    'PHONE': re.compile(r'(?:\+91[\-\s]?)?[6-9]\d{9}\b'),
    'TXN_REF': re.compile(r'\b(?:UTR|UPI|TXN|REF|IMPS|NEFT)[\s/:\-_#]*([0-9A-Z]{8,22})\b|\b([0-9]{12})\b', re.IGNORECASE),
    'AMOUNT': re.compile(r'(?:₹|INR|Rs\.?|INR\s*|Rs\s*)\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?|[0-9]+(?:\.[0-9]{2})?)', re.IGNORECASE),
    'DATE': re.compile(r'\b(?:\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b', re.IGNORECASE),
    'URL_DOMAIN': re.compile(r'https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)|\b([a-zA-Z0-9-]+\.(?:com|org|in|net|xyz|top|ru|co|biz|info))\b', re.IGNORECASE),
}

def extract_metadata_from_image(file_path):
    """Extract EXIF and image properties using Pillow."""
    metadata = {}
    try:
        with Image.open(file_path) as img:
            metadata['format'] = img.format
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['mode'] = img.mode
            
            exif_data = img._getexif()
            if exif_data:
                exif_dict = {}
                for tag_id, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    # Avoid serializing raw byte structures
                    if isinstance(value, (bytes, bytearray)):
                        continue
                    exif_dict[tag_name] = str(value)
                metadata['exif'] = exif_dict
                if 'DateTimeOriginal' in exif_dict:
                    metadata['creation_date'] = exif_dict['DateTimeOriginal']
                if 'Model' in exif_dict:
                    metadata['device_model'] = exif_dict['Model']
    except Exception as e:
        metadata['error'] = str(e)
    return metadata

def extract_metadata_from_pdf(file_path):
    """Extract PDF document properties using PyMuPDF."""
    metadata = {}
    try:
        doc = fitz.open(file_path)
        metadata['page_count'] = len(doc)
        doc_meta = doc.metadata or {}
        for k, v in doc_meta.items():
            if v:
                metadata[k] = str(v)
        doc.close()
    except Exception as e:
        metadata['error'] = str(e)
    return metadata

def extract_text_from_file(file_path, file_type):
    """
    Extracts text according to file type:
    - PDF: PyMuPDF page-by-page extraction, or OCR if scanned.
    - Image: pytesseract OCR (with fallback diagnostics).
    - Text: safe character decode.
    """
    results = []
    
    if file_type == 'pdf':
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text and len(text.strip()) > 10:
                    results.append({
                        'page': page_num + 1,
                        'method': 'PDF_NATIVE_TEXT',
                        'text': text.strip(),
                        'quality_score': 0.98,
                        'notes': 'Direct vector/native text extraction'
                    })
                else:
                    # Page seems scanned or has no text, attempt OCR on page pixmap
                    ocr_attempted = False
                    try:
                        pix = page.get_pixmap(dpi=150)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        ocr_text = pytesseract.image_to_string(img)
                        if ocr_text and len(ocr_text.strip()) > 5:
                            results.append({
                                'page': page_num + 1,
                                'method': 'PDF_SCANNED_OCR',
                                'text': ocr_text.strip(),
                                'quality_score': 0.85,
                                'notes': 'Optical Character Recognition via Tesseract on rasterized page'
                            })
                            ocr_attempted = True
                    except Exception as ocr_err:
                        pass
                    
                    if not ocr_attempted:
                        results.append({
                            'page': page_num + 1,
                            'method': 'PDF_EMPTY_OR_UNREADABLE',
                            'text': text.strip() if text else '',
                            'quality_score': 0.3,
                            'notes': 'Low extraction quality: Scanned page without accessible OCR text. Manual review required.'
                        })
            doc.close()
        except Exception as e:
            results.append({
                'page': 1,
                'method': 'PDF_EXTRACTION_ERROR',
                'text': '',
                'quality_score': 0.0,
                'notes': f'Error reading PDF: {str(e)}'
            })

    elif file_type == 'image':
        ocr_text = ""
        ocr_success = False
        notes = ""
        quality_score = 0.85

        try:
            with Image.open(file_path) as img:
                ocr_text = pytesseract.image_to_string(img)
                if ocr_text.strip():
                    ocr_success = True
                    notes = "Optical Character Recognition (pytesseract) successful"
                else:
                    notes = "Image processed by OCR but no discernible text characters were recognized."
                    quality_score = 0.4
        except pytesseract.TesseractNotFoundError:
            quality_score = 0.3
            notes = "Tesseract OCR binary not installed on host PATH. Flagged for investigator manual inspection."
        except Exception as e:
            quality_score = 0.2
            notes = f"OCR engine error: {str(e)}"

        results.append({
            'page': 1,
            'method': 'IMAGE_OCR' if ocr_success else 'IMAGE_METADATA_ONLY',
            'text': ocr_text.strip(),
            'quality_score': quality_score,
            'notes': notes
        })

    elif file_type == 'text':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            results.append({
                'page': 1,
                'method': 'SAFE_TXT_READ',
                'text': content.strip(),
                'quality_score': 1.0,
                'notes': 'UTF-8 decoded raw text'
            })
        except Exception as e:
            results.append({
                'page': 1,
                'method': 'TXT_READ_ERROR',
                'text': '',
                'quality_score': 0.0,
                'notes': str(e)
            })

    return results

def extract_entities_from_text(text):
    """
    Identifies structured cybercrime entities via Regex patterns + spaCy NER.
    Returns list of dicts: {'type': ..., 'value': ..., 'normalized': ..., 'confidence': ...}
    """
    extracted = []
    seen = set()

    if not text:
        return extracted

    # 1. Regex Extraction
    # UPI IDs
    for match in PATTERNS['UPI_ID'].finditer(text):
        val = match.group().strip()
        norm = val.lower()
        if ('UPI_ID', norm) not in seen:
            seen.add(('UPI_ID', norm))
            extracted.append({
                'type': 'UPI_ID',
                'value': val,
                'normalized': norm,
                'confidence': 0.98,
                'context': text[max(0, match.start()-30):min(len(text), match.end()+30)].replace('\n', ' ')
            })

    # Phone numbers
    for match in PATTERNS['PHONE'].finditer(text):
        val = match.group().strip()
        norm = re.sub(r'[\s\-\+]', '', val)
        if norm.startswith('91') and len(norm) == 12:
            norm = norm[2:]
        if len(norm) == 10 and ('PHONE', norm) not in seen:
            seen.add(('PHONE', norm))
            extracted.append({
                'type': 'PHONE',
                'value': val,
                'normalized': norm,
                'confidence': 0.95,
                'context': text[max(0, match.start()-30):min(len(text), match.end()+30)].replace('\n', ' ')
            })

    # Emails
    for match in PATTERNS['EMAIL'].finditer(text):
        val = match.group().strip()
        norm = val.lower()
        if ('EMAIL', norm) not in seen:
            seen.add(('EMAIL', norm))
            extracted.append({
                'type': 'EMAIL',
                'value': val,
                'normalized': norm,
                'confidence': 0.98,
                'context': text[max(0, match.start()-30):min(len(text), match.end()+30)].replace('\n', ' ')
            })

    # Transaction References
    for match in PATTERNS['TXN_REF'].finditer(text):
        val = match.group(1) or match.group(2) or match.group(0)
        val = val.strip().replace(' ', '')
        if len(val) >= 8:
            norm = val.upper()
            if ('TXN_REF', norm) not in seen:
                seen.add(('TXN_REF', norm))
                extracted.append({
                    'type': 'TXN_REF',
                    'value': val,
                    'normalized': norm,
                    'confidence': 0.92,
                    'context': text[max(0, match.start()-30):min(len(text), match.end()+30)].replace('\n', ' ')
                })

    # Amounts
    for match in PATTERNS['AMOUNT'].finditer(text):
        raw_amt = match.group(1).replace(',', '').strip()
        try:
            amt_float = float(raw_amt)
            if amt_float > 0:
                norm = f"{amt_float:.2f}"
                if ('AMOUNT', norm) not in seen:
                    seen.add(('AMOUNT', norm))
                    extracted.append({
                        'type': 'AMOUNT',
                        'value': f"₹{match.group(1).strip()}",
                        'normalized': norm,
                        'confidence': 0.90,
                        'context': text[max(0, match.start()-30):min(len(text), match.end()+30)].replace('\n', ' ')
                    })
        except ValueError:
            pass

    # Dates
    for match in PATTERNS['DATE'].finditer(text):
        val = match.group().strip()
        norm = val
        if ('DATE', norm) not in seen:
            seen.add(('DATE', norm))
            extracted.append({
                'type': 'DATE',
                'value': val,
                'normalized': norm,
                'confidence': 0.88,
                'context': text[max(0, match.start()-30):min(len(text), match.end()+30)].replace('\n', ' ')
            })

    # URLs & Suspicious Domains
    for match in PATTERNS['URL_DOMAIN'].finditer(text):
        val = match.group().strip()
        norm = val.lower().replace('https://', '').replace('http://', '').split('/')[0]
        if norm and ('URL_DOMAIN', norm) not in seen:
            seen.add(('URL_DOMAIN', norm))
            extracted.append({
                'type': 'URL_DOMAIN',
                'value': val,
                'normalized': norm,
                'confidence': 0.94,
                'context': text[max(0, match.start()-30):min(len(text), match.end()+30)].replace('\n', ' ')
            })

    # 2. spaCy NER (Named Entities: Persons, Organizations, Locations)
    if nlp and len(text) > 10:
        try:
            doc = nlp(text[:10000]) # Cap to avoid overhead on massive texts
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE']:
                    val = ent.text.strip()
                    norm = val.title()
                    # Filter out short or junk terms
                    if len(val) > 2 and ('ENTITY_' + ent.label_, norm) not in seen:
                        # Avoid common stop/bank terms misidentified as persons
                        if norm.lower() in ['bank', 'india', 'state', 'phone', 'screenshot', 'account', 'dear', 'sir']:
                            continue
                        seen.add(('ENTITY_' + ent.label_, norm))
                        extracted.append({
                            'type': f"SUSPECT_{ent.label_}",
                            'value': val,
                            'normalized': norm,
                            'confidence': 0.85,
                            'context': f"spaCy recognized {ent.label_}: {val}"
                        })
        except Exception:
            pass

    return extracted

def process_evidence_file(evidence_id, db):
    """
    Main extraction pipeline for an individual evidence file:
    1. Extract file properties & metadata (EXIF / PDF)
    2. Extract text (Native or OCR)
    3. Run structured entity extraction
    4. Store results into database
    5. Record analysis run
    """
    file_row = db.execute("SELECT * FROM evidence_files WHERE id = ?", (evidence_id,)).fetchone()
    if not file_row:
        return {'status': 'error', 'message': 'Evidence file not found'}

    case_id = file_row['case_id']
    file_path = file_row['file_path']
    file_type = file_row['file_type']

    # 1. Metadata extraction
    if file_type == 'image':
        metadata = extract_metadata_from_image(file_path)
    elif file_type == 'pdf':
        metadata = extract_metadata_from_pdf(file_path)
    else:
        metadata = {'file_type': 'text'}

    db.execute(
        "UPDATE evidence_files SET metadata_json = ? WHERE id = ?",
        (json.dumps(metadata), evidence_id)
    )

    # 2. Text extraction
    extracted_records = extract_text_from_file(file_path, file_type)
    
    # Clear previous extractions for this file to avoid duplicates on re-analysis
    db.execute("DELETE FROM extracted_text WHERE evidence_id = ?", (evidence_id,))
    db.execute("DELETE FROM entities WHERE evidence_id = ?", (evidence_id,))
    db.execute("DELETE FROM entity_evidence_links WHERE evidence_id = ?", (evidence_id,))

    all_file_text = []
    for rec in extracted_records:
        all_file_text.append(rec['text'])
        db.execute("""
            INSERT INTO extracted_text (
                evidence_id, case_id, extraction_method, source_page,
                text_content, quality_score, quality_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            evidence_id, case_id, rec['method'], rec['page'],
            rec['text'], rec['quality_score'], rec['notes']
        ))

    combined_text = "\n".join(all_file_text)

    # 3. Entity extraction
    entities = extract_entities_from_text(combined_text)
    for ent in entities:
        cursor = db.execute("""
            INSERT INTO entities (
                case_id, evidence_id, entity_type, entity_value,
                normalized_value, context, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id, evidence_id, ent['type'], ent['value'],
            ent['normalized'], ent['context'], ent['confidence']
        ))
        entity_id = cursor.lastrowid
        
        # Link entity to evidence file
        db.execute("""
            INSERT OR REPLACE INTO entity_evidence_links (
                entity_id, evidence_id, case_id, mention_count
            ) VALUES (?, ?, ?, 1)
        """, (entity_id, evidence_id, case_id))

    # 4. Record analysis run
    db.execute("""
        INSERT INTO analysis_runs (
            case_id, evidence_id, status, tool_versions, started_at, completed_at
        ) VALUES (?, ?, 'completed', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (case_id, evidence_id, "PyMuPDF, spaCy, Pillow, PyTesseract"))
    
    db.commit()
    return {
        'status': 'success',
        'text_blocks': len(extracted_records),
        'entities_found': len(entities),
        'metadata': metadata
    }
