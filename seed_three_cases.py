import sqlite3
import hashlib
from config import Config

def seed():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("Cleaning up database and preparing exactly 3 demo cases...")

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Clear old cases beyond 3 if any
    cursor.execute("DELETE FROM cases WHERE id > 3")
    
    # We will reset and accurately populate cases 1, 2, 3
    # First, clear child tables for cases 1, 2, 3 so there are no orphan/mixed records
    cursor.execute("DELETE FROM findings WHERE case_id IN (1, 2, 3)")
    cursor.execute("DELETE FROM events WHERE case_id IN (1, 2, 3)")
    cursor.execute("DELETE FROM entities WHERE case_id IN (1, 2, 3)")
    cursor.execute("DELETE FROM extracted_text WHERE case_id IN (1, 2, 3)")
    cursor.execute("DELETE FROM evidence_files WHERE case_id IN (1, 2, 3)")
    cursor.execute("DELETE FROM cases WHERE id IN (1, 2, 3)")

    # Ensure users exist
    # User 1: Insp. Sharma (Investigator)
    # User 2: Sneha Reddy (Citizen - Case 1)
    # User 3: Aarav Patel (Citizen - Case 2)
    # User 4: Rajesh Kumar (Citizen - Case 3)
    users_to_ensure = [
        (1, 'inv_sharma', 'investigator@cybershield.gov.in', 'scrypt:32768:8:1$demo$inv', 'Inspector R. Sharma', 'investigator', '+91 9811223344', 'CYB-INV-709'),
        (2, 'sneha_reddy', 'sneha.reddy@example.com', 'scrypt:32768:8:1$demo$cit', 'Sneha Reddy', 'citizen', '+91 9123456780', None),
        (3, 'aarav_patel', 'aarav.patel@example.com', 'scrypt:32768:8:1$demo$cit', 'Aarav Patel', 'citizen', '+91 9822334455', None),
        (4, 'rajesh_kumar', 'rajesh.kumar@example.com', 'scrypt:32768:8:1$demo$cit', 'Rajesh Kumar', 'citizen', '+91 7766554433', None)
    ]
    for u in users_to_ensure:
        cursor.execute("""
            INSERT OR REPLACE INTO users (id, username, email, password_hash, full_name, role, phone, badge_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, u)

    # =========================================================================
    # CASE 1: PENDING TO BE VERIFIED (Under Review)
    # Title: Telegram VIP Crypto Doubling & Task Scheme Fraud
    # Loss: ₹75,000
    # =========================================================================
    cursor.execute("""
        INSERT INTO cases (
            id, case_id, user_id, title, category, description,
            incident_date, reported_date, loss_amount, suspect_phone,
            suspect_email, suspect_upi, suspect_platform, status, priority
        ) VALUES (
            1, 'CS-2026-28410', 2,
            'Telegram VIP Crypto Doubling & Task Scheme Fraud',
            'Financial Fraud',
            'Victim was approached via Telegram offering high returns for rating videos and depositing USDT tokens. After initial mock payouts, ₹75,000 was deposited to suspect UPI ''vip_crypto_admin@icici'', after which withdrawals were frozen with demand for additional clearance fees. Case is pending investigator verification.',
            '2026-10-07 14:30:00', '2026-10-08 10:15:00',
            75000.0, '+91 91234 56789', 'support@viptask-crypto.pro',
            'vip_crypto_admin@icici', 'Telegram',
            'Under Review', 'High'
        )
    """)

    # Evidence for Case 1
    cursor.execute("""
        INSERT INTO evidence_files (
            id, case_id, uploader_id, original_filename, stored_filename,
            file_path, file_size, mime_type, sha256_hash, upload_time, file_type, is_readonly
        ) VALUES
        (1, 1, 2, 'Telegram_VIP_Group_Chat.txt', 'ev_c1_f1.txt', 'uploads/ev_c1_f1.txt', 1240, 'text/plain',
         'b4571e95a129db50f18b99471ee4a988623925595445f36d30ace51d42f29332', '2026-10-08 10:18:00', 'TXT', 1),
        (2, 1, 2, 'Paytm_Transfer_Vouchers.pdf', 'ev_c1_f2.pdf', 'uploads/ev_c1_f2.pdf', 3840, 'application/pdf',
         'a4d9994be8e67a25a4b7b864abcf42e404d62715f1056524ed4d65a3039c2551', '2026-10-08 10:19:30', 'PDF', 1)
    """)

    # Extracted Text for Case 1
    cursor.execute("""
        INSERT INTO extracted_text (evidence_id, case_id, extraction_method, source_page, text_content, quality_score, quality_notes)
        VALUES
        (1, 1, 'Text Parser & spaCy NER', 1, 
         '[07/10/26 11:15 AM] VIP Admin: Welcome to Daily Crypto Task Group! Earn 25% daily ROI.\n[07/10/26 01:40 PM] VIP Admin: Send 75000 INR to vip_crypto_admin@icici to unlock Gold VIP withdrawals. Call admin on +91 91234 56789.', 0.95, 'Clear unencrypted transcript'),
        (2, 1, 'Direct Stream Extraction (PyMuPDF)', 1,
         'PAYTM PAYMENT CONFIRMATION\nPaid to: VIP CRYPTO GLOBAL\nUPI ID: vip_crypto_admin@icici\nAmount: INR 75,000.00\nTxn Ref: PAYTM9982736182\nStatus: SUCCESS', 0.98, 'Digital PDF stream extract')
    """)

    # Entities for Case 1
    cursor.execute("""
        INSERT INTO entities (case_id, evidence_id, entity_type, entity_value, normalized_value, context, confidence)
        VALUES
        (1, 1, 'PHONE', '+91 91234 56789', '+919123456789', 'Call admin on +91 91234 56789', 0.96),
        (1, 1, 'UPI_ID', 'vip_crypto_admin@icici', 'vip_crypto_admin@icici', 'Send 75000 INR to vip_crypto_admin@icici', 0.99),
        (1, 2, 'UPI_ID', 'vip_crypto_admin@icici', 'vip_crypto_admin@icici', 'Paid to: VIP CRYPTO GLOBAL UPI: vip_crypto_admin@icici', 0.99),
        (1, 2, 'AMOUNT', '₹75,000.00', '75000.00', 'Amount: INR 75,000.00', 0.98),
        (1, 2, 'TRANSACTION_ID', 'PAYTM9982736182', 'PAYTM9982736182', 'Txn Ref: PAYTM9982736182', 0.97)
    """)

    # Findings for Case 1 (Pending Verification)
    cursor.execute("""
        INSERT INTO findings (case_id, category, severity, title, explanation, rule_name, status)
        VALUES
        (1, 'VERIFICATION_PENDING', 'HIGH', 'Forensic Counterparty Check Pending', 'Submitted payment voucher and chat log require counter-verification against receiving nodal bank beneficiary account.', 'RULE_PENDING_REVIEW', 'Open'),
        (1, 'UNAUTHORIZED_SCHEME', 'MEDIUM', 'Unlicensed High-Yield Crypto Solicit', 'Suspect group solicits capital investments with promise of 25% daily ROI in violation of financial regulations.', 'RULE_ILLEGAL_SOLICIT', 'Open')
    """)

    # Events for Case 1
    cursor.execute("""
        INSERT INTO events (case_id, evidence_id, title, event_date, event_time, description, confidence, verification_status)
        VALUES
        (1, 1, 'Initial Telegram Solicit', '2026-10-07', '11:15 AM', 'Victim contacted via Telegram group offering video rating rewards.', 0.92, 'Single Source'),
        (1, 1, 'Mock Reward Credited', '2026-10-07', '01:40 PM', 'Victim received fake screenshot of ₹500 credited to induce trust.', 0.90, 'Unverified'),
        (1, 2, 'Transferred ₹75,000 to VIP Admin', '2026-10-07', '02:30 PM', 'Victim transferred ₹75,000 via Paytm UPI to vip_crypto_admin@icici (Txn PAYTM9982736182).', 0.97, 'Corroborated'),
        (1, 1, 'Withdrawal Blocked & Demand for Clearance', '2026-10-07', '04:00 PM', 'Scammer locked victim account and demanded additional ₹30,000 clearance fee.', 0.95, 'Single Source')
    """)

    # =========================================================================
    # CASE 2: EVIDENCE VERIFIED
    # Title: OLX Camera Advance Payment Scam & Fake GPay Slip
    # Loss: ₹25,000
    # =========================================================================
    cursor.execute("""
        INSERT INTO cases (
            id, case_id, user_id, title, category, description,
            incident_date, reported_date, loss_amount, suspect_phone,
            suspect_email, suspect_upi, suspect_platform, status, priority
        ) VALUES (
            2, 'CS-2026-10492', 3,
            'OLX Camera Advance Payment Scam & Fake GPay Slip',
            'Online Payment Fraud',
            'Victim agreed to purchase Sony A7 IV camera on OLX for ₹40,000. Scammer requested ₹25,000 advance on GPay to merchant VPA ''fake_merchant_scam@okaxis''. After payment was made and debit statement issued, seller blocked communication and demanded additional insurance fees.',
            '2026-10-09 16:15:00', '2026-10-10 11:30:00',
            25000.0, '+91 98765 43210', 'seller.deals.olx@gmail.com',
            'fake_merchant_scam@okaxis', 'OLX / WhatsApp',
            'Evidence Verified', 'High'
        )
    """)

    # Evidence for Case 2
    cursor.execute("""
        INSERT INTO evidence_files (
            id, case_id, uploader_id, original_filename, stored_filename,
            file_path, file_size, mime_type, sha256_hash, upload_time, file_type, is_readonly
        ) VALUES
        (3, 2, 3, 'GPay_Debit_Screenshot_25k.png', 'ev_c2_f1.png', 'uploads/ev_c2_f1.png', 18739, 'image/png',
         '7fee92a3e475e2f38d388659101d2d5d8b877f8045f4fa7b789a5ad3041eebe5', '2026-10-10 11:35:00', 'PNG', 1),
        (4, 2, 3, 'Bank_Debit_Statement_October.pdf', 'ev_c2_f2.pdf', 'uploads/ev_c2_f2.pdf', 3280, 'application/pdf',
         '38f1d6a17a4c6a461e89b37c02b36e89ee65902e86bc059a43a0eeb9e3b44b82', '2026-10-10 11:36:12', 'PDF', 1),
        (5, 2, 3, 'OLX_WhatsApp_Chat_Export.txt', 'ev_c2_f3.txt', 'uploads/ev_c2_f3.txt', 1024, 'text/plain',
         '6b9e985439b48c6ef060e9845f949e87f9d2ed7c85b1f369409a2d2fd2668d0c', '2026-10-10 11:37:05', 'TXT', 1)
    """)

    # Extracted Text for Case 2
    cursor.execute("""
        INSERT INTO extracted_text (evidence_id, case_id, extraction_method, source_page, text_content, quality_score, quality_notes)
        VALUES
        (3, 2, 'OCR (Tesseract v5)', 1,
         'Google Pay • Payment Successful\nPaid to: Manoj Sharma (Electronics Store)\nUPI ID: fake_merchant_scam@okaxis\nAmount: ₹25,000.00\nDate: 09 Oct 2026, 04:15 PM\nUPI Transaction ID: 428901928401\nGoogle Transaction ID: CICAgODf_8enEQ', 0.96, 'High clarity screenshot'),
        (4, 2, 'Direct Stream Extraction (PyMuPDF)', 1,
         'HDFC BANK ACCOUNT STATEMENT\nAccount: XXXXXXXX4912\nTxn Date: 09-10-2026 16:18:22\nNarration: UPI/428901928401/fake_merchant_scam/Payment to merchant\nWithdrawal (DR): INR 25,000.00\nClosing Balance: INR 1,42,850.50', 1.00, 'Exact digital ledger extraction'),
        (5, 2, 'Text Parser & spaCy NER', 1,
         '[09/10/26, 3:45 PM] Scammer: Pay 25000 advance on GPay to fake_merchant_scam@okaxis to confirm Sony A7 IV camera courier.\n[09/10/26, 3:50 PM] Victim: Sent payment screenshot. Call me on +91 98765 43210.\n[09/10/26, 4:25 PM] Scammer: System blocked you need to pay 15000 more for insurance.', 1.00, 'Direct message stream')
    """)

    # Entities for Case 2
    cursor.execute("""
        INSERT INTO entities (case_id, evidence_id, entity_type, entity_value, normalized_value, context, confidence)
        VALUES
        (2, 3, 'UPI_ID', 'fake_merchant_scam@okaxis', 'fake_merchant_scam@okaxis', 'Paid to: UPI ID fake_merchant_scam@okaxis', 0.99),
        (2, 3, 'AMOUNT', '₹25,000.00', '25000.00', 'Amount: ₹25,000.00', 0.98),
        (2, 3, 'TRANSACTION_ID', '428901928401', '428901928401', 'UPI Transaction ID: 428901928401', 0.97),
        (2, 4, 'UPI_ID', 'fake_merchant_scam@okaxis', 'fake_merchant_scam@okaxis', 'Narration: UPI/428901928401/fake_merchant_scam', 1.00),
        (2, 4, 'AMOUNT', '₹25,000.00', '25000.00', 'Withdrawal (DR): INR 25,000.00', 1.00),
        (2, 4, 'TRANSACTION_ID', '428901928401', '428901928401', 'Narration: UPI/428901928401', 1.00),
        (2, 5, 'PHONE', '+91 98765 43210', '+919876543210', 'Call me on +91 98765 43210', 0.98),
        (2, 5, 'UPI_ID', 'fake_merchant_scam@okaxis', 'fake_merchant_scam@okaxis', 'Pay 25000 advance on GPay to fake_merchant_scam@okaxis', 0.99)
    """)

    # Findings for Case 2 (Evidence Verified)
    cursor.execute("""
        INSERT INTO findings (case_id, category, severity, title, explanation, rule_name, status)
        VALUES
        (2, 'MATCH_CONFIRMED', 'HIGH', 'Transaction ID Multi-Exhibit Match', 'Transaction reference 428901928401 matches identically in Google Pay receipt and Official Bank statement.', 'RULE_TXN_MATCH', 'Verified'),
        (2, 'CORROBORATED', 'MEDIUM', 'Merchant VPA Solicit Alert', 'WhatsApp chat export explicitly reveals suspect directing payment to fake_merchant_scam@okaxis.', 'RULE_VPA_SOLICIT', 'Verified')
    """)

    # Events for Case 2
    cursor.execute("""
        INSERT INTO events (case_id, evidence_id, title, event_date, event_time, description, confidence, verification_status)
        VALUES
        (2, 5, 'Initial Scammer Contact via WhatsApp', '2026-10-09', '03:45 PM', 'Suspect contacted complainant offering Sony A7 IV camera for ₹25,000 advance payment.', 0.98, 'Corroborated'),
        (2, 3, 'Google Pay Transfer of ₹25,000 Executed', '2026-10-09', '04:15 PM', 'Complainant executed UPI payment to fake_merchant_scam@okaxis with UTR 428901928401.', 0.99, 'Corroborated'),
        (2, 4, 'HDFC Bank Ledger Recorded ₹25,000 Debit', '2026-10-09', '04:18 PM', 'Bank account statement confirms debit with matching UTR 428901928401.', 1.00, 'Corroborated'),
        (2, 5, 'Communication Severed & Extortion Attempt', '2026-10-09', '04:25 PM', 'Scammer demanded secondary ₹15,000 courier insurance before blocking phone number.', 0.96, 'Single Source')
    """)

    # =========================================================================
    # CASE 3: ALREADY COMPLETED (Completed)
    # Title: Bank KYC Phishing SMS & Unauthorized IMPS Transfer
    # Loss: ₹12,000
    # =========================================================================
    cursor.execute("""
        INSERT INTO cases (
            id, case_id, user_id, title, category, description,
            incident_date, reported_date, loss_amount, suspect_phone,
            suspect_email, suspect_upi, suspect_platform, status, priority
        ) VALUES (
            3, 'CS-2026-39148', 4,
            'Bank KYC Phishing SMS & Unauthorized IMPS Transfer',
            'Phishing & Identity Theft',
            'Victim received urgent SMS alleging SBI account suspension within 24 hours. Clicked phishing link (sbi-kyc-verify.online) and entered netbanking credentials and OTP. ₹12,000 unauthorized IMPS transfer executed to unknown beneficiary. Investigation concluded and bank nodal freeze alert executed.',
            '2026-10-05 09:20:00', '2026-10-06 09:00:00',
            12000.0, '+91 98111 22334', 'admin@sbi-kyc-verify.online',
            'sbi_kyc_verify@upi', 'SMS / Phishing Site',
            'Completed', 'Medium'
        )
    """)

    # Evidence for Case 3
    cursor.execute("""
        INSERT INTO evidence_files (
            id, case_id, uploader_id, original_filename, stored_filename,
            file_path, file_size, mime_type, sha256_hash, upload_time, file_type, is_readonly
        ) VALUES
        (6, 3, 4, 'Phishing_SMS_Text_Log.txt', 'ev_c3_f1.txt', 'uploads/ev_c3_f1.txt', 850, 'text/plain',
         '7846d836b3b61e89c4f1ecf58eb513712876ff0b1a9fc3b455782d2d60149d57', '2026-10-06 09:15:00', 'TXT', 1),
        (7, 3, 4, 'Bank_IMPS_Unauthorized_Debit.pdf', 'ev_c3_f2.pdf', 'uploads/ev_c3_f2.pdf', 4500, 'application/pdf',
         'f0e1d2c3b4a5968778695a4b3c2d1e0f0123456789abcdef0123456789abcdef', '2026-10-06 09:16:30', 'PDF', 1)
    """)

    # Extracted Text for Case 3
    cursor.execute("""
        INSERT INTO extracted_text (evidence_id, case_id, extraction_method, source_page, text_content, quality_score, quality_notes)
        VALUES
        (6, 3, 'Text Parser & spaCy NER', 1,
         'URGENT: Your SBI Account will be blocked today. Update KYC immediately at https://sbi-kyc-verify.online or contact +91 98111 22334.', 0.98, 'Raw SMS transcript from device'),
        (7, 3, 'Direct Stream Extraction (PyMuPDF)', 1,
         'ACCOUNT TRANSACTION ALERT\nDebit: INR 12,000.00\nChannel: IMPS Instant Transfer\nBeneficiary: UNKNOWN BENEFICIARY\nTxn UTR: IMPS910283746501\nTimestamp: 05-10-2026 09:20:14', 1.00, 'Banking alert ledger extract')
    """)

    # Entities for Case 3
    cursor.execute("""
        INSERT INTO entities (case_id, evidence_id, entity_type, entity_value, normalized_value, context, confidence)
        VALUES
        (3, 6, 'PHONE', '+91 98111 22334', '+919811122334', 'contact +91 98111 22334', 0.99),
        (3, 6, 'URL', 'https://sbi-kyc-verify.online', 'sbi-kyc-verify.online', 'Update KYC immediately at https://sbi-kyc-verify.online', 0.98),
        (3, 7, 'AMOUNT', '₹12,000.00', '12000.00', 'Debit: INR 12,000.00', 1.00),
        (3, 7, 'TRANSACTION_ID', 'IMPS910283746501', 'IMPS910283746501', 'Txn UTR: IMPS910283746501', 1.00)
    """)

    # Findings for Case 3 (Already Completed)
    cursor.execute("""
        INSERT INTO findings (case_id, category, severity, title, explanation, rule_name, status)
        VALUES
        (3, 'PHISHING_CONFIRMED', 'HIGH', 'Malicious Phishing Portal Identified', 'Extracted URL sbi-kyc-verify.online flagged as fraudulent credential harvester. Domain takedown served.', 'RULE_PHISHING_DOMAIN', 'Resolved'),
        (3, 'INVESTIGATION_CONCLUDED', 'LOW', 'Forensic Audit Complete & Bank Freeze Filed', 'All digital evidence verified, hash signatures cryptographically sealed, and report delivered for beneficiary account recovery.', 'RULE_CASE_CLOSED', 'Resolved')
    """)

    # Events for Case 3
    cursor.execute("""
        INSERT INTO events (case_id, evidence_id, title, event_date, event_time, description, confidence, verification_status)
        VALUES
        (3, 6, 'Phishing SMS Received', '2026-10-05', '09:05 AM', 'Victim received spoofed SMS warning of imminent SBI account suspension.', 0.98, 'Corroborated'),
        (3, 6, 'Phishing Portal Visited & Credentials Entered', '2026-10-05', '09:12 AM', 'Victim entered netbanking password and SMS OTP on fraudulent domain.', 0.95, 'Corroborated'),
        (3, 7, 'Unauthorized IMPS Transfer Deducted (₹12,000)', '2026-10-05', '09:20 AM', 'Immediate unauthorized transfer completed with UTR IMPS910283746501.', 1.00, 'Corroborated'),
        (3, 7, 'Investigation Completed & Final Dossier Delivered', '2026-10-06', '11:00 AM', 'Investigation concluded with full digital forensics summary and bank freeze request.', 1.00, 'Verified')
    """)

    conn.commit()
    conn.close()
    print("Database seeding completed successfully! Exactly 3 clean demo cases configured:")
    print("  Case 1: Under Review (Pending to be verified) - Telegram VIP Crypto & Task Scheme (Loss: INR 75,000)")
    print("  Case 2: Evidence Verified (Verified) - OLX Camera Advance Payment Scam (Loss: INR 25,000)")
    print("  Case 3: Completed (Already Completed) - Bank KYC Phishing SMS & Unauthorized IMPS Transfer (Loss: INR 12,000)")

if __name__ == '__main__':
    seed()
