import os
import io
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont
from werkzeug.security import generate_password_hash
from database import get_standalone_db, init_db
from config import Config
from modules.evidence import save_and_record_evidence
from modules.extraction import process_evidence_file
from modules.verification import run_cross_evidence_verification
from modules.timeline import reconstruct_case_timeline
from modules.audit import log_audit

class DummyFile:
    """Wraps bytes to simulate Flask/Werkzeug FileStorage for seeding."""
    def __init__(self, filename, content_bytes):
        self.filename = filename
        self._bytes = content_bytes
        self._io = io.BytesIO(content_bytes)

    def read(self, *args):
        return self._io.read(*args)

def create_sample_pdf(title, text_blocks):
    """Generates a text-rich PDF in-memory using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4
    y = 50
    page.insert_text((50, y), title, fontsize=16, fontname="helv", color=(0.1, 0.2, 0.6))
    y += 30
    for block in text_blocks:
        page.insert_text((50, y), block, fontsize=10, fontname="helv", color=(0.15, 0.15, 0.15))
        y += 20
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def create_sample_receipt_image(title, details_lines):
    """Generates a realistic receipt screenshot image using Pillow."""
    img = Image.new('RGB', (600, 420), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    # Header banner
    draw.rectangle([(0, 0), (600, 60)], fill=(37, 99, 235))
    draw.text((20, 20), title, fill=(255, 255, 255))

    y = 85
    for line in details_lines:
        draw.text((30, y), line, fill=(30, 41, 59))
        y += 32

    # Footer note
    draw.line([(30, 370), (570, 370)], fill=(203, 213, 225), width=1)
    draw.text((30, 385), "Transaction processed securely via Instant Payment Network", fill=(100, 116, 139))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def seed_database():
    print("Beginning CyberShield Database Seeding...")
    init_db()
    db = get_standalone_db()

    # 1. Seed Controlled Demo Users
    users_data = [
        ('investigator@cybershield.local', 'inv_sharma', 'Inspector R. Sharma', 'investigator', 'investigator123', '+91 9811223344', 'CYB-INV-709'),
        ('citizen@cybershield.local', 'aarav_patel', 'Aarav Patel (Victim)', 'citizen', 'citizen123', '+91 9822334455', None),
        ('admin@cybershield.local', 'chief_admin', 'Chief System Administrator', 'admin', 'admin123', '+91 9900112233', 'ADMIN-HQ-01'),
        ('neha.sharma@example.com', 'neha_s', 'Neha Sharma', 'citizen', 'citizen123', '+91 8877665544', None),
        ('rajesh.k@example.com', 'rajesh_k', 'Rajesh Kumar', 'citizen', 'citizen123', '+91 7766554433', None)
    ]

    user_ids = {}
    for email, username, fullname, role, pwd, phone, badge in users_data:
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            user_ids[email] = existing['id']
        else:
            pwd_hash = generate_password_hash(pwd)
            cursor = db.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, phone, badge_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, email, pwd_hash, fullname, role, phone, badge))
            user_ids[email] = cursor.lastrowid
    db.commit()
    print("Users initialized.")

    # 2. Case 1: UPI QR Code Scam
    c1 = db.execute("SELECT id FROM cases WHERE case_id = 'CS-2026-10492'").fetchone()
    if not c1:
        cursor = db.execute("""
            INSERT INTO cases (
                case_id, user_id, title, category, description, incident_date,
                loss_amount, suspect_phone, suspect_email, suspect_upi, suspect_platform,
                status, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'CS-2026-10492', user_ids['citizen@cybershield.local'],
            'Fraudulent OLX Buyer QR Code Payment Theft',
            'Online Payment Fraud / UPI Scam',
            'I listed a wooden sofa set on OLX for Rs 45,000. The buyer claiming to be Vikram Singh from the Indian Army contacted me on WhatsApp (+91 9823145670). He claimed he wanted to reserve the sofa and sent a QR code stating "Scan this QR code and enter UPI PIN to receive advance deposit of Rs 45,000 in your bank account". When I scanned and entered PIN, instead of receiving money, Rs 25,000 was debited immediately to UPI ID vikram.store98@okaxis with UTR 928172645102. When I objected, he claimed a technical glitch and asked me to scan another code of Rs 20,000 to reverse it, which also got debited with UTR 928172645103.',
            '2026-10-08',
            45000.00,
            '+91 9823145670',
            'support.armydeal@gmail.com',
            'vikram.store98@okaxis',
            'OLX & WhatsApp',
            'Evidence Verified',
            'High'
        ))
        c1_id = cursor.lastrowid
        db.commit()

        # Add Evidence Files for Case 1
        # A. WhatsApp Chat log
        chat_content = """[08/10/26, 14:15:10] Vikram Singh: Hello Sir, I saw your OLX listing for sofa set Rs 45,000. Is it available?
[08/10/26, 14:16:02] Aarav Patel: Yes available. Where are you located?
[08/10/26, 14:18:22] Vikram Singh: I am posted at Military Camp. I will buy it today itself. My contact number is +91 9823145670.
[08/10/26, 14:22:45] Vikram Singh: I am transferring full advance Rs 45,000 through army merchant account.
[08/10/26, 14:24:12] Vikram Singh: Please scan this military merchant QR code for UPI ID vikram.store98@okaxis.
[08/10/26, 14:26:00] Vikram Singh: It will show pay option, just type your UPI PIN to authenticate deposit receipt.
[08/10/26, 14:28:15] Aarav Patel: Hey! Rs 25,000 debited from my HDFC bank with UTR 928172645102! Why money went out?
[08/10/26, 14:29:40] Vikram Singh: Sir don't panic, army server error occurred. Scan second refund code for Rs 20,000.
[08/10/26, 14:32:05] Aarav Patel: Second Rs 20,000 also deducted with UTR 928172645103! You are a fraud!
[08/10/26, 14:33:00] Vikram Singh: *User blocked you*"""
        
        f1 = DummyFile("OLX_WhatsApp_Chat_Export.txt", chat_content.encode('utf-8'))
        ev1_id, _ = save_and_record_evidence(f1, c1_id, user_ids['citizen@cybershield.local'], db)
        process_evidence_file(ev1_id, db)

        # B. Official Bank Statement PDF
        pdf1_bytes = create_sample_pdf(
            "HDFC BANK — ACCOUNT TRANSACTION STATEMENT",
            [
                "Account Holder: Aarav Patel | Account No: XXXX-XXXX-5521",
                "Statement Period: 01-Oct-2026 to 09-Oct-2026 | Generated on 09-Oct-2026",
                "--------------------------------------------------------------------------------",
                "Date: 08-Oct-2026 | Debit Amount: INR 25,000.00",
                "Narration: UPI/928172645102/Payment to vikram.store98@okaxis/HDFC0001",
                "Transaction Status: SUCCESS | Available Balance: INR 12,450.00",
                "--------------------------------------------------------------------------------",
                "Date: 08-Oct-2026 | Debit Amount: INR 20,000.00",
                "Narration: UPI/928172645103/Transfer to vikram.store98@okaxis/AXIS0009",
                "Transaction Status: SUCCESS | Available Balance: INR -7,550.00 (Overdraft)",
                "Total Loss Claimed: INR 45,000.00 across 2 transactions."
            ]
        )
        f2 = DummyFile("Bank_Debit_Statement_October.pdf", pdf1_bytes)
        ev2_id, _ = save_and_record_evidence(f2, c1_id, user_ids['citizen@cybershield.local'], db)
        process_evidence_file(ev2_id, db)

        # C. Payment App Receipt Image
        img1_bytes = create_sample_receipt_image(
            "Google Pay — Transaction Receipt",
            [
                "Paid to: Vikram Military Store (vikram.store98@okaxis)",
                "Amount: Rs 25,000.00",
                "Date & Time: 08 Oct 2026, 02:27 PM",
                "UPI Transaction ID: 928172645102",
                "Sender Phone: +91 9822334455",
                "Beneficiary Phone: +91 9823145670",
                "Status: Completed"
            ]
        )
        f3 = DummyFile("GPay_Debit_Screenshot_25k.png", img1_bytes)
        ev3_id, _ = save_and_record_evidence(f3, c1_id, user_ids['citizen@cybershield.local'], db)
        process_evidence_file(ev3_id, db)

        # Run verification & timeline
        run_cross_evidence_verification(c1_id, db)
        reconstruct_case_timeline(c1_id, db)

        # Add initial investigator observation note
        db.execute("""
            INSERT INTO investigator_notes (case_id, investigator_id, note_type, content)
            VALUES (?, ?, 'Triage Recommendation', ?)
        """, (
            c1_id, user_ids['investigator@cybershield.local'],
            "Evidence inventory exhibits strong cross-corroboration. Beneficiary UPI ID vikram.store98@okaxis and phone +91 9823145670 match across chat export, bank statement, and payment screenshot. UTR references 928172645102 and 928172645103 are documented. Cumulative debits match claimed ₹45,000 loss exactly. Recommending immediate bank nodal liaison to freeze beneficiary account at Axis Bank."
        ))
        db.commit()

    # 3. Case 2: Telegram Work From Home Scam
    c2 = db.execute("SELECT id FROM cases WHERE case_id = 'CS-2026-21804'").fetchone()
    if not c2:
        cursor = db.execute("""
            INSERT INTO cases (
                case_id, user_id, title, category, description, incident_date,
                loss_amount, suspect_phone, suspect_email, suspect_upi, suspect_platform,
                status, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'CS-2026-21804', user_ids['neha.sharma@example.com'],
            'Telegram Part-Time YouTube Rating Investment Scam',
            'Work-From-Home / Investment Scam',
            'Received an unsolicited WhatsApp message offering part time work for rating YouTube videos. Paid initial bonus of Rs 500 to win trust. Then instructed to join Telegram group @GlobalMediaTaskGroup managed by admin @Pooja_Task_Manager (Phone +91 8876543219). Made to pay Rs 12,000, then Rs 30,000, and Rs 40,000 to UPI growcapital.invest@paytm for VIP crypto arbitrage task. Account portal showed fake balance of Rs 1,80,000 but withdrawal was rejected demanding Rs 50,000 tax clearance.',
            '2026-10-05',
            82000.00,
            '+91 8876543219',
            'support@globalmediatasks.org',
            'growcapital.invest@paytm',
            'Telegram & WhatsApp',
            'Under Review',
            'High'
        ))
        c2_id = cursor.lastrowid
        db.commit()

        # Evidence files for Case 2
        chat2_content = """Telegram Messenger Chat Export
Target Group: @GlobalMediaTaskGroup
Admin: Pooja Sharma (@Pooja_Task_Manager | Mobile: +91 8876543219)
Victim: Neha Sharma (+91 8877665544)

[05/10/2026 11:20:15] Admin: Welcome to VIP Tier 2 Trading. To unlock 40% payout, transfer investment to growcapital.invest@paytm.
[05/10/2026 11:35:40] Neha: Sent Rs 12,000 via Paytm UPI. UTR is 884719203948.
[05/10/2026 12:45:00] Admin: Order requires combo fund deposit of Rs 30,000 to same UPI growcapital.invest@paytm.
[05/10/2026 13:10:12] Neha: Sent Rs 30,000. UTR is 884719203949. Please process withdrawal.
[05/10/2026 14:05:22] Admin: Final merchant clearance deposit of Rs 40,000 needed. UTR must be shared within 15 minutes.
[05/10/2026 14:25:30] Neha: Transferred Rs 40,000. UTR is 884719203950. Total Rs 82,000 invested!
[05/10/2026 15:00:10] Admin: System error 404: Pay 30% government TDS Rs 50,000 to release Rs 1,80,000 profit.
[05/10/2026 15:15:00] Neha: I do not have more money! Please refund my principal Rs 82,000."""
        
        f4 = DummyFile("Telegram_VIP_Group_Chat.txt", chat2_content.encode('utf-8'))
        ev4_id, _ = save_and_record_evidence(f4, c2_id, user_ids['neha.sharma@example.com'], db)
        process_evidence_file(ev4_id, db)

        pdf2_bytes = create_sample_pdf(
            "PAYTM PAYMENTS BANK — CONSOLIDATED DEBIT RECEIPTS",
            [
                "Account Holder: Neha Sharma | Customer ID: PPB-992144",
                "Recipient: GROW CAPITAL CONSULTING (growcapital.invest@paytm)",
                "--------------------------------------------------------------------------------",
                "Transaction 1: 05-Oct-2026 11:35 AM | Amount: INR 12,000.00 | UTR: 884719203948",
                "Transaction 2: 05-Oct-2026 01:10 PM | Amount: INR 30,000.00 | UTR: 884719203949",
                "Transaction 3: 05-Oct-2026 02:25 PM | Amount: INR 40,000.00 | UTR: 884719203950",
                "--------------------------------------------------------------------------------",
                "Cumulative Outflow: INR 82,000.00 | Beneficiary Bank: Paytm Payments Bank Ltd."
            ]
        )
        f5 = DummyFile("Paytm_Transfer_Vouchers.pdf", pdf2_bytes)
        ev5_id, _ = save_and_record_evidence(f5, c2_id, user_ids['neha.sharma@example.com'], db)
        process_evidence_file(ev5_id, db)

        run_cross_evidence_verification(c2_id, db)
        reconstruct_case_timeline(c2_id, db)

    # 4. Case 3: Phishing Banking SMS
    c3 = db.execute("SELECT id FROM cases WHERE case_id = 'CS-2026-34710'").fetchone()
    if not c3:
        cursor = db.execute("""
            INSERT INTO cases (
                case_id, user_id, title, category, description, incident_date,
                loss_amount, suspect_phone, suspect_email, suspect_upi, suspect_platform,
                status, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'CS-2026-34710', user_ids['rajesh.k@example.com'],
            'SBI YONO KYC Block Phishing Portal Fraud',
            'Phishing & Credential Harvesting',
            'Received an urgent SMS: "Dear Customer, your State Bank account will be suspended today due to unverified PAN. Update your KYC immediately at http://sbi-kyc-verify-portal.xyz to avoid deactivation". Clicked the link, which opened an exact replica of SBI YONO login screen. Entered netbanking credentials and OTP sent to mobile. Immediately received debit notification of Rs 1,15,000 transferred via IMPS reference IMPS617283940192 to unknown account.',
            '2026-10-09',
            115000.00,
            '+91 7012345678',
            'alert@sbi-kyc-verify-portal.xyz',
            'None (Direct Netbanking IMPS)',
            'Phishing SMS & Website',
            'Submitted',
            'High'
        ))
        c3_id = cursor.lastrowid
        db.commit()

        sms_content = """Extracted SMS Header and Message Content
Sender ID: AD-SBIKYC
Timestamp: 09/10/2026 09:42:15 AM
Destination: +91 7766554433 (Rajesh Kumar)

Message:
"Dear SBI Customer, your YONO Netbanking is locked due to pending KYC mandate. 
Click http://sbi-kyc-verify-portal.xyz to update PAN & Aadhaar immediately. 
Helpline: +91 7012345678. - SBI Support Team"

Debit Alert Received Shortly After:
"Rs 1,15,000.00 debited from A/c XX4091 on 09-10-26 10:15:22 via IMPS Ref IMPS617283940192.
Beneficiary: QuickPay Tech. Balance: Rs 4,200.00"
"""
        f6 = DummyFile("Phishing_SMS_Text_Log.txt", sms_content.encode('utf-8'))
        ev6_id, _ = save_and_record_evidence(f6, c3_id, user_ids['rajesh.k@example.com'], db)
        process_evidence_file(ev6_id, db)

        run_cross_evidence_verification(c3_id, db)
        reconstruct_case_timeline(c3_id, db)

    db.close()
    print("CyberShield Database Seeding Completed Successfully!")

if __name__ == '__main__':
    seed_database()
