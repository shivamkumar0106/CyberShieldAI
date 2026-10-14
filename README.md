# CyberShield AI — Cybercrime Reporting & Digital Evidence Investigation Platform

CyberShield is a web-based cybercrime reporting and digital evidence investigation-support platform. It combines cybercrime complaint management with automated evidence extraction, integrity verification, incident timeline reconstruction, and interactive relationship analysis.

> **Important Boundary & Scope:**
> CyberShield assists an investigation; it does **not** replace a cybercrime investigator, forensic laboratory, or official police reporting system. 
> There is no custom black-box ML model, no automated guilt verdict, and no claim of perfect deepfake detection. 
> Accepted evidence files are treated as strictly read-only and preserved with cryptographic SHA-256 digests.

---

## Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (Fetch API), Bootstrap 5, Bootstrap Icons, Cytoscape.js
- **Backend:** Python 3.14 / Flask
- **Database:** SQLite (12 normalized tables with foreign keys and indexes)
- **Text & Metadata Extraction:** PyMuPDF (`pymupdf`), Pillow (`PIL`), PyTesseract (OCR)
- **Entity Extraction & NER:** spaCy (`en_core_web_sm`) + Custom Cybercrime Regex (UPI IDs, Phones, UTRs, Amounts, Emails, URLs)
- **Integrity & Reports:** Cryptographic SHA-256 digests + ReportLab PDF generation

---

## Core Modules

1. **Module 1 — Authentication & Access Control:**
   - Role-based separation for **Citizens** and **Investigators/Admins**.
   - Werkzeug secure password hashing and session handling.
   - 1-Click Instant Demo Login for evaluation.

2. **Module 2 — Complaint & Case Management:**
   - Categorized complaint intake: UPI Fraud, Phishing, Identity Theft, Social Media Extortion, Investment Scams.
   - Unique Case ID generation (e.g. `CS-2026-10492`).
   - Incident narrative, transaction details, and status lifecycle tracking.

3. **Module 3 — Evidence Upload & Cryptographic Integrity:**
   - Multi-format support: `JPG`, `JPEG`, `PNG`, `PDF`, `TXT`.
   - Byte-level SHA-256 hash calculated immediately upon intake.
   - Read-only storage permissions to prevent modification.
   - Live real-time tamper verification with disk hash recalculation.

4. **Module 4 — Evidence Extraction:**
   - Native text extraction from PDFs via PyMuPDF.
   - Optical Character Recognition (OCR) for screenshots.
   - Image EXIF metadata parsing (capture date, camera/software).
   - Structured entity extraction: UPI IDs, Phone Numbers, 12-digit UTRs, Transaction IDs, Amounts (₹), Emails, and Domains.

5. **Module 5 — Cross-Evidence Verification Engine:**
   - Deterministic explainable rules:
     - `RULE_SHA256_HASH_VERIFY`: Cryptographic file integrity status.
     - `RULE_CROSS_FILE_MATCH`: Correlates suspect identifiers found across multiple files.
     - `RULE_COMPLAINT_EVIDENCE_CORRELATION`: Matches suspect details in complaint form with evidence artifacts.
     - `RULE_AMOUNT_CORROBORATION` & `DISCREPANCY_FLAG`: Compares claimed loss against extracted receipts.
     - `RULE_PAYMENT_CORE_EVIDENCE_GAP`: Flags missing banking statements or UTR identifiers for payment fraud.

6. **Module 6 — Incident Timeline Reconstruction:**
   - Chronologically orders incident initiation, communication events, file creation timestamps, transactions, and complaint registration.
   - Source file attribution and confidence scoring.

7. **Module 7 — Evidence Relationship Graph:**
   - Interactive Cytoscape.js network visualizer.
   - Color-coded nodes (Cases, Files, Entities: UPI, Phone, UTR, Amount, Events).
   - Layout switches (Force-directed CoSE, Concentric, Circle, Hierarchical).
   - Click-to-inspect sidebar showing extracted attributes and source citations.

8. **Module 8 — Investigation Dashboard & PDF Dossier:**
   - Metrics KPI cards and categorized case triage.
   - One-click ReportLab PDF dossier generation with forensic disclaimers, evidence inventory hashes, rule findings, and timeline.
   - System-wide append-only audit trail logging all actions with client IP and timestamps.

---

## Controlled Demo Accounts

You can log in manually or use the **"Quick Demo Access"** dropdown in the navigation bar:

| Role | Email / Username | Password | Purpose |
|---|---|---|---|
| **Investigator** | `investigator@cybershield.local` | `investigator123` | Full investigation workbench, Cytoscape graph, re-run analysis, PDF export |
| **Citizen / Victim** | `citizen@cybershield.local` | `citizen123` | Lodge complaints, upload files, track personal case status |
| **Administrator** | `admin@cybershield.local` | `admin123` | System oversight and full audit log inspection |

---

## Pre-Loaded Test Scenarios

The system comes pre-seeded with 3 realistic cybercrime cases and genuine sample digital evidence files:

1. **`CS-2026-10492` — OLX QR Code Advance Payment Scam**
   - Complainant: Aarav Patel | Loss: ₹45,000.00
   - Evidence: WhatsApp chat log, HDFC debit statement PDF (UTRs `928172645102` & `928172645103`), GPay receipt screenshot PNG.
   - Suspect UPI: `vikram.store98@okaxis` | Phone: `+91 9823145670`.

2. **`CS-2026-21804` — Telegram YouTube Like Investment Scam**
   - Complainant: Neha Sharma | Loss: ₹82,000.00
   - Evidence: Telegram chat export, Paytm consolidated payment voucher PDF.
   - Suspect UPI: `growcapital.invest@paytm` | Phone: `+91 8876543219`.

3. **`CS-2026-34710` — SBI YONO KYC Block Phishing Portal**
   - Complainant: Rajesh Kumar | Loss: ₹1,15,000.00
   - Evidence: Phishing SMS text log with link `http://sbi-kyc-verify-portal.xyz`, IMPS reference `IMPS617283940192`.

---

## Running the Application

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Seed Initial Database & Evidence Files:**
   ```bash
   python seed_data.py
   ```

3. **Start Flask Development Server:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to: **`http://127.0.0.1:5000`**

4. **Run Automated Test Suite:**
   ```bash
   python -m unittest test_cybershield.py
   ```
