// ==========================================================================
// CyberShield — Analysis & Extraction Controller
// ==========================================================================

const CyberShieldAnalysis = {
    demoExtractions: [
        {
            evidence_name: "Telegram_VIP_Group_Chat.txt (Case 1: Pending)",
            method: "Text Parser & spaCy NER",
            quality_score: 95,
            raw_text: "[07/10/26 11:15 AM] VIP Admin: Welcome to Daily Crypto Task Group! Earn 25% daily ROI.\n[07/10/26 01:40 PM] VIP Admin: Send 75000 INR to vip_crypto_admin@icici to unlock Gold VIP withdrawals. Call admin on +91 91234 56789.",
            entities: [
                { type: "PHONE", value: "+91 91234 56789", confidence: "0.96" },
                { type: "UPI_ID", value: "vip_crypto_admin@icici", confidence: "0.99" },
                { type: "AMOUNT", value: "₹75,000.00", confidence: "0.98" }
            ]
        },
        {
            evidence_name: "GPay_Debit_Screenshot_25k.png (Case 2: Verified)",
            method: "OCR (Tesseract v5)",
            quality_score: 96,
            raw_text: "Google Pay • Payment Successful\nPaid to: Manoj Sharma (Electronics Store)\nUPI ID: fake_merchant_scam@okaxis\nAmount: ₹25,000.00\nDate: 09 Oct 2026, 04:15 PM\nUPI Transaction ID: 428901928401\nGoogle Transaction ID: CICAgODf_8enEQ",
            entities: [
                { type: "UPI_ID", value: "fake_merchant_scam@okaxis", confidence: "0.99" },
                { type: "AMOUNT", value: "₹25,000.00", confidence: "0.98" },
                { type: "TRANSACTION_ID", value: "428901928401", confidence: "0.95" },
                { type: "DATE", value: "09 Oct 2026, 04:15 PM", confidence: "0.94" }
            ]
        },
        {
            evidence_name: "Bank_Debit_Statement_October.pdf (Case 2: Verified)",
            method: "Direct Stream Extraction (PyMuPDF)",
            quality_score: 100,
            raw_text: "HDFC BANK ACCOUNT STATEMENT\nAccount: XXXXXXXX4912\nTxn Date: 09-10-2026 16:18:22\nNarration: UPI/428901928401/fake_merchant_scam/Payment to merchant\nWithdrawal (DR): INR 25,000.00\nClosing Balance: INR 1,42,850.50",
            entities: [
                { type: "UPI_ID", value: "fake_merchant_scam@okaxis", confidence: "1.00" },
                { type: "AMOUNT", value: "₹25,000.00", confidence: "1.00" },
                { type: "TRANSACTION_ID", value: "428901928401", confidence: "1.00" },
                { type: "DATE", value: "09-10-2026 16:18:22", confidence: "1.00" }
            ]
        },
        {
            evidence_name: "Phishing_SMS_Text_Log.txt (Case 3: Completed)",
            method: "Text Parser & spaCy NER",
            quality_score: 98,
            raw_text: "URGENT: Your SBI Account will be blocked today. Update KYC immediately at https://sbi-kyc-verify.online or contact +91 98111 22334.",
            entities: [
                { type: "PHONE", value: "+91 98111 22334", confidence: "0.99" },
                { type: "URL", value: "https://sbi-kyc-verify.online", confidence: "0.98" }
            ]
        }
    ],

    init() {
        this.render();
    },

    render() {
        const container = document.getElementById('analysisCardsContainer');
        if (!container) return;

        container.innerHTML = this.demoExtractions.map(item => `
            <div class="analysis-doc-card">
                <div class="doc-card-header">
                    <div class="doc-meta">
                        <i class="fa-solid fa-file-invoice text-blue"></i>
                        <span class="font-bold text-dark">${item.evidence_name}</span>
                        <span class="badge-method">${item.method}</span>
                    </div>
                    <div class="doc-score">
                        <span class="score-label">OCR Quality:</span>
                        <span class="score-pill score-high">${item.quality_score}%</span>
                    </div>
                </div>

                <div class="analysis-body-grid">
                    <!-- Extracted Text Raw Box -->
                    <div class="text-stream-box">
                        <div class="box-title">EXTRACTED TEXT STREAM</div>
                        <pre class="raw-text-content font-mono">${item.raw_text}</pre>
                    </div>

                    <!-- Entity Badges -->
                    <div class="entities-cloud-box">
                        <div class="box-title">IDENTIFIED ENTITIES (NER & REGEX)</div>
                        <div class="entity-pills-wrap">
                            ${item.entities.map(e => `
                                <div class="entity-pill pill-${e.type.toLowerCase()}">
                                    <span class="entity-type font-mono">${e.type}</span>
                                    <span class="entity-val font-mono font-bold">${e.value}</span>
                                    <span class="entity-conf">${Math.round(parseFloat(e.confidence)*100)}%</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    CyberShieldAnalysis.init();
});
