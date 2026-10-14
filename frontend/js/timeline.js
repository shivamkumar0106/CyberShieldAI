// ==========================================================================
// CyberShield — Incident Timeline Controller
// ==========================================================================

const CyberShieldTimeline = {
    caseEvents: {
        1: {
            case_id: "CS-2026-28410",
            title: "Telegram VIP Crypto Doubling & Task Scheme Fraud",
            events: [
                {
                    time: "07 Oct 2026, 11:15 AM",
                    title: "Initial Telegram Solicit",
                    desc: "Victim contacted via Telegram group offering video rating rewards.",
                    source_file: "Telegram_VIP_Group_Chat.txt",
                    source_type: "Chat Log",
                    status: "Single Source",
                    badge_class: "status-pending"
                },
                {
                    time: "07 Oct 2026, 01:40 PM",
                    title: "Mock Reward Credited",
                    desc: "Victim received fake screenshot of ₹500 credited to induce trust.",
                    source_file: "Telegram_VIP_Group_Chat.txt",
                    source_type: "Chat Log",
                    status: "Unverified",
                    badge_class: "status-pending"
                },
                {
                    time: "07 Oct 2026, 02:30 PM",
                    title: "Transferred ₹75,000 to VIP Admin",
                    desc: "Victim transferred ₹75,000 via Paytm UPI to vip_crypto_admin@icici (Txn PAYTM9982736182).",
                    source_file: "Paytm_Transfer_Vouchers.pdf",
                    source_type: "Payment Slip",
                    status: "Corroborated",
                    badge_class: "status-verified"
                },
                {
                    time: "07 Oct 2026, 04:00 PM",
                    title: "Withdrawal Blocked & Demand for Clearance",
                    desc: "Scammer locked victim account and demanded additional ₹30,000 clearance fee.",
                    source_file: "Telegram_VIP_Group_Chat.txt",
                    source_type: "Chat Log",
                    status: "Single Source",
                    badge_class: "status-pending"
                }
            ]
        },
        2: {
            case_id: "CS-2026-10492",
            title: "OLX Camera Advance Payment Scam & Fake GPay Slip",
            events: [
                {
                    time: "09 Oct 2026, 03:45 PM",
                    title: "Scammer Contact via WhatsApp",
                    desc: "Impersonator contacted victim offering Sony A7 IV camera courier for ₹25,000 advance payment.",
                    source_file: "OLX_WhatsApp_Chat_Export.txt",
                    source_type: "Chat Log",
                    status: "Corroborated",
                    badge_class: "status-verified"
                },
                {
                    time: "09 Oct 2026, 04:15 PM",
                    title: "GPay Payment Executed (₹25,000)",
                    desc: "Victim initiated UPI transaction via Google Pay to 'fake_merchant_scam@okaxis' with Ref #428901928401.",
                    source_file: "GPay_Debit_Screenshot_25k.png",
                    source_type: "OCR Screenshot",
                    status: "Corroborated",
                    badge_class: "status-verified"
                },
                {
                    time: "09 Oct 2026, 04:18 PM",
                    title: "HDFC Core Banking Debit Confirmed",
                    desc: "Bank core ledger recorded debit of ₹25,000 with matching UPI UTR 428901928401.",
                    source_file: "Bank_Debit_Statement_October.pdf",
                    source_type: "Bank Statement",
                    status: "Corroborated",
                    badge_class: "status-verified"
                },
                {
                    time: "09 Oct 2026, 04:25 PM",
                    title: "Secondary Extortion Attempt (₹15,000)",
                    desc: "Scammer demanded additional ₹15,000 alleging courier insurance lockdown before severing contact.",
                    source_file: "OLX_WhatsApp_Chat_Export.txt",
                    source_type: "Chat Log",
                    status: "Single Source",
                    badge_class: "status-pending"
                }
            ]
        },
        3: {
            case_id: "CS-2026-39148",
            title: "Bank KYC Phishing SMS & Unauthorized IMPS Transfer",
            events: [
                {
                    time: "05 Oct 2026, 09:05 AM",
                    title: "Phishing SMS Received",
                    desc: "Victim received spoofed SMS warning of imminent SBI account suspension.",
                    source_file: "Phishing_SMS_Text_Log.txt",
                    source_type: "SMS Log",
                    status: "Corroborated",
                    badge_class: "status-verified"
                },
                {
                    time: "05 Oct 2026, 09:12 AM",
                    title: "Phishing Portal Visited & Credentials Entered",
                    desc: "Victim entered netbanking password and SMS OTP on fraudulent domain.",
                    source_file: "Phishing_SMS_Text_Log.txt",
                    source_type: "Web Portal",
                    status: "Corroborated",
                    badge_class: "status-verified"
                },
                {
                    time: "05 Oct 2026, 09:20 AM",
                    title: "Unauthorized IMPS Transfer Deducted (₹12,000)",
                    desc: "Immediate unauthorized transfer completed with UTR IMPS910283746501.",
                    source_file: "Bank_IMPS_Unauthorized_Debit.pdf",
                    source_type: "Bank Statement",
                    status: "Corroborated",
                    badge_class: "status-verified"
                },
                {
                    time: "06 Oct 2026, 11:00 AM",
                    title: "Investigation Completed & Final Dossier Delivered",
                    desc: "Investigation concluded with full digital forensics summary and bank freeze request.",
                    source_file: "CyberShield Report",
                    source_type: "Audit Record",
                    status: "Verified",
                    badge_class: "status-verified"
                }
            ]
        }
    },

    init() {
        const urlParams = new URLSearchParams(window.location.search);
        let idParam = parseInt(urlParams.get('id'));
        if (!idParam || !this.caseEvents[idParam]) {
            idParam = 1;
        }
        this.render(idParam);
    },

    render(caseId) {
        const caseData = this.caseEvents[caseId] || this.caseEvents[1];
        
        const badgeEl = document.querySelector('.header-count-badge');
        if (badgeEl) {
            badgeEl.innerHTML = `CASE REF: ${caseData.case_id}`;
        }

        const list = document.getElementById('timelineContainer');
        if (!list) return;

        list.innerHTML = caseData.events.map((ev) => `
            <div class="timeline-step-item">
                <div class="timeline-milestone-marker">
                    <div class="marker-dot"></div>
                    <div class="marker-line"></div>
                </div>

                <div class="timeline-step-card">
                    <div class="timeline-card-header">
                        <div class="timeline-time-badge font-mono">
                            <i class="fa-regular fa-clock"></i> ${ev.time}
                        </div>
                        <span class="status-pill ${ev.badge_class}">${ev.status}</span>
                    </div>

                    <h3 class="timeline-event-title">${ev.title}</h3>
                    <p class="timeline-event-desc">${ev.desc}</p>

                    <div class="timeline-source-footer">
                        <span class="source-label">Source Evidence:</span>
                        <span class="source-badge font-mono">
                            <i class="fa-regular fa-file"></i> ${ev.source_file} (${ev.source_type})
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    CyberShieldTimeline.init();
});
