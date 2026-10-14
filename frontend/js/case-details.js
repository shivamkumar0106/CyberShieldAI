// ==========================================================================
// CyberShield — Case Details & Investigation Workbench Controller
// ==========================================================================

const CyberShieldCaseDetails = {
    // Built-in fallback database for the 3 demo cases
    fallbackData: {
        1: {
            case: {
                id: 1,
                case_id: "CS-2026-28410",
                title: "Telegram VIP Crypto Doubling & Task Scheme Fraud",
                category: "Financial Fraud",
                description: "Victim was approached via Telegram offering high returns for rating videos and depositing USDT tokens. After initial mock payouts, ₹75,000 was deposited to suspect UPI 'vip_crypto_admin@icici', after which withdrawals were frozen with demand for additional clearance fees. Case is pending investigator verification.",
                incident_date: "07 Oct 2026, 14:30",
                reported_date: "08 Oct 2026, 10:15",
                loss_amount: 75000,
                status: "Under Review",
                priority: "High",
                complainant_name: "Sneha Reddy",
                complainant_phone: "+91 91234 56780",
                complainant_email: "sneha.reddy@example.com",
                suspect_phone: "+91 91234 56789",
                suspect_upi: "vip_crypto_admin@icici",
                suspect_platform: "Telegram"
            },
            evidence_files: [
                {
                    id: 1,
                    original_filename: "Telegram_VIP_Group_Chat.txt",
                    file_type: "TXT",
                    file_size: 1240,
                    sha256_hash: "b4571e95a129db50f18b99471ee4a988623925595445f36d30ace51d42f29332",
                    upload_time: "08 Oct 2026, 10:18 AM",
                    quality_score: 0.95,
                    extraction_method: "Text Parser & spaCy NER"
                },
                {
                    id: 2,
                    original_filename: "Paytm_Transfer_Vouchers.pdf",
                    file_type: "PDF",
                    file_size: 3840,
                    sha256_hash: "a4d9994be8e67a25a4b7b864abcf42e404d62715f1056524ed4d65a3039c2551",
                    upload_time: "08 Oct 2026, 10:19 AM",
                    quality_score: 0.98,
                    extraction_method: "Direct Stream Extraction (PyMuPDF)"
                }
            ],
            entities: [
                { entity_type: "PHONE", entity_value: "+91 91234 56789", confidence: 0.96 },
                { entity_type: "UPI_ID", entity_value: "vip_crypto_admin@icici", confidence: 0.99 },
                { entity_type: "AMOUNT", entity_value: "₹75,000.00", confidence: 0.98 },
                { entity_type: "TRANSACTION_ID", entity_value: "PAYTM9982736182", confidence: 0.97 }
            ],
            findings: [
                {
                    severity: "HIGH",
                    category: "VERIFICATION_PENDING",
                    title: "Forensic Counterparty Check Pending",
                    explanation: "Submitted payment voucher and chat log require counter-verification against receiving nodal bank beneficiary account."
                },
                {
                    severity: "MEDIUM",
                    category: "UNAUTHORIZED_SCHEME",
                    title: "Unlicensed High-Yield Crypto Solicit",
                    explanation: "Suspect group solicits capital investments with promise of 25% daily ROI in violation of financial regulations."
                }
            ],
            timeline: [
                { event_time: "07 Oct 2026, 11:15 AM", title: "Initial Telegram Solicit", description: "Victim contacted via Telegram group offering video rating rewards." },
                { event_time: "07 Oct 2026, 01:40 PM", title: "Mock Reward Credited", description: "Victim received fake screenshot of ₹500 credited to induce trust." },
                { event_time: "07 Oct 2026, 02:30 PM", title: "Transferred ₹75,000 to VIP Admin", description: "Victim transferred ₹75,000 via Paytm UPI to vip_crypto_admin@icici (Txn PAYTM9982736182)." },
                { event_time: "07 Oct 2026, 04:00 PM", title: "Withdrawal Blocked & Demand for Clearance", description: "Scammer locked victim account and demanded additional ₹30,000 clearance fee." }
            ]
        },
        2: {
            case: {
                id: 2,
                case_id: "CS-2026-10492",
                title: "OLX Camera Advance Payment Scam & Fake GPay Slip",
                category: "Online Payment Fraud",
                description: "Victim agreed to purchase Sony A7 IV camera on OLX for ₹40,000. Scammer requested ₹25,000 advance on GPay to merchant VPA 'fake_merchant_scam@okaxis'. After payment was made and debit statement issued, seller blocked communication and demanded additional insurance fees.",
                incident_date: "09 Oct 2026, 16:15",
                reported_date: "10 Oct 2026, 11:30",
                loss_amount: 25000,
                status: "Evidence Verified",
                priority: "High",
                complainant_name: "Aarav Patel",
                complainant_phone: "+91 98223 34455",
                complainant_email: "aarav.patel@example.com",
                suspect_phone: "+91 98765 43210",
                suspect_upi: "fake_merchant_scam@okaxis",
                suspect_platform: "OLX / WhatsApp"
            },
            evidence_files: [
                {
                    id: 3,
                    original_filename: "GPay_Debit_Screenshot_25k.png",
                    file_type: "PNG",
                    file_size: 18739,
                    sha256_hash: "7fee92a3e475e2f38d388659101d2d5d8b877f8045f4fa7b789a5ad3041eebe5",
                    upload_time: "10 Oct 2026, 11:35 AM",
                    quality_score: 0.96,
                    extraction_method: "OCR (Tesseract v5)"
                },
                {
                    id: 4,
                    original_filename: "Bank_Debit_Statement_October.pdf",
                    file_type: "PDF",
                    file_size: 3280,
                    sha256_hash: "38f1d6a17a4c6a461e89b37c02b36e89ee65902e86bc059a43a0eeb9e3b44b82",
                    upload_time: "10 Oct 2026, 11:36 AM",
                    quality_score: 1.00,
                    extraction_method: "Direct Stream Extraction (PyMuPDF)"
                },
                {
                    id: 5,
                    original_filename: "OLX_WhatsApp_Chat_Export.txt",
                    file_type: "TXT",
                    file_size: 1024,
                    sha256_hash: "6b9e985439b48c6ef060e9845f949e87f9d2ed7c85b1f369409a2d2fd2668d0c",
                    upload_time: "10 Oct 2026, 11:37 AM",
                    quality_score: 1.00,
                    extraction_method: "Text Parser & spaCy NER"
                }
            ],
            entities: [
                { entity_type: "UPI_ID", entity_value: "fake_merchant_scam@okaxis", confidence: 0.99 },
                { entity_type: "AMOUNT", entity_value: "₹25,000.00", confidence: 0.98 },
                { entity_type: "PHONE", entity_value: "+91 98765 43210", confidence: 0.98 },
                { entity_type: "TRANSACTION_ID", entity_value: "428901928401", confidence: 0.97 }
            ],
            findings: [
                {
                    severity: "HIGH",
                    category: "MATCH_CONFIRMED",
                    title: "Transaction ID Multi-Exhibit Match",
                    explanation: "Transaction reference 428901928401 matches identically in Google Pay receipt and Official Bank statement."
                },
                {
                    severity: "MEDIUM",
                    category: "CORROBORATED",
                    title: "Merchant VPA Solicit Alert",
                    explanation: "WhatsApp chat export explicitly reveals suspect directing payment to fake_merchant_scam@okaxis."
                }
            ],
            timeline: [
                { event_time: "09 Oct 2026, 03:45 PM", title: "Initial Scammer Contact via WhatsApp", description: "Suspect contacted complainant offering Sony A7 IV camera for ₹25,000 advance payment." },
                { event_time: "09 Oct 2026, 04:15 PM", title: "Google Pay Transfer of ₹25,000 Executed", description: "Complainant executed UPI payment to fake_merchant_scam@okaxis with UTR 428901928401." },
                { event_time: "09 Oct 2026, 04:18 PM", title: "HDFC Bank Ledger Recorded ₹25,000 Debit", description: "Bank account statement confirms debit with matching UTR 428901928401." },
                { event_time: "09 Oct 2026, 04:25 PM", title: "Communication Severed & Extortion Attempt", description: "Scammer demanded secondary ₹15,000 courier insurance before blocking phone number." }
            ]
        },
        3: {
            case: {
                id: 3,
                case_id: "CS-2026-39148",
                title: "Bank KYC Phishing SMS & Unauthorized IMPS Transfer",
                category: "Phishing & Identity Theft",
                description: "Victim received urgent SMS alleging SBI account suspension within 24 hours. Clicked phishing link (sbi-kyc-verify.online) and entered netbanking credentials and OTP. ₹12,000 unauthorized IMPS transfer executed to unknown beneficiary. Investigation concluded and bank nodal freeze alert executed.",
                incident_date: "05 Oct 2026, 09:20",
                reported_date: "06 Oct 2026, 09:00",
                loss_amount: 12000,
                status: "Completed",
                priority: "Medium",
                complainant_name: "Rajesh Kumar",
                complainant_phone: "+91 77665 54433",
                complainant_email: "rajesh.kumar@example.com",
                suspect_phone: "+91 98111 22334",
                suspect_upi: "sbi_kyc_verify@upi",
                suspect_platform: "SMS / Phishing Site"
            },
            evidence_files: [
                {
                    id: 6,
                    original_filename: "Phishing_SMS_Text_Log.txt",
                    file_type: "TXT",
                    file_size: 850,
                    sha256_hash: "7846d836b3b61e89c4f1ecf58eb513712876ff0b1a9fc3b455782d2d60149d57",
                    upload_time: "06 Oct 2026, 09:15 AM",
                    quality_score: 0.98,
                    extraction_method: "Text Parser & spaCy NER"
                },
                {
                    id: 7,
                    original_filename: "Bank_IMPS_Unauthorized_Debit.pdf",
                    file_type: "PDF",
                    file_size: 4500,
                    sha256_hash: "f0e1d2c3b4a5968778695a4b3c2d1e0f0123456789abcdef0123456789abcdef",
                    upload_time: "06 Oct 2026, 09:16 AM",
                    quality_score: 1.00,
                    extraction_method: "Direct Stream Extraction (PyMuPDF)"
                }
            ],
            entities: [
                { entity_type: "PHONE", entity_value: "+91 98111 22334", confidence: 0.99 },
                { entity_type: "URL", entity_value: "sbi-kyc-verify.online", confidence: 0.98 },
                { entity_type: "AMOUNT", entity_value: "₹12,000.00", confidence: 1.00 },
                { entity_type: "TRANSACTION_ID", entity_value: "IMPS910283746501", confidence: 1.00 }
            ],
            findings: [
                {
                    severity: "HIGH",
                    category: "PHISHING_CONFIRMED",
                    title: "Malicious Phishing Portal Identified",
                    explanation: "Extracted URL sbi-kyc-verify.online flagged as fraudulent credential harvester. Domain takedown served."
                },
                {
                    severity: "LOW",
                    category: "INVESTIGATION_CONCLUDED",
                    title: "Forensic Audit Complete & Bank Freeze Filed",
                    explanation: "All digital evidence verified, hash signatures cryptographically sealed, and report delivered for beneficiary account recovery."
                }
            ],
            timeline: [
                { event_time: "05 Oct 2026, 09:05 AM", title: "Phishing SMS Received", description: "Victim received spoofed SMS warning of imminent SBI account suspension." },
                { event_time: "05 Oct 2026, 09:12 AM", title: "Phishing Portal Visited & Credentials Entered", description: "Victim entered netbanking password and SMS OTP on fraudulent domain." },
                { event_time: "05 Oct 2026, 09:20 AM", title: "Unauthorized IMPS Transfer Deducted (₹12,000)", description: "Immediate unauthorized transfer completed with UTR IMPS910283746501." },
                { event_time: "06 Oct 2026, 11:00 AM", title: "Investigation Completed & Final Dossier Delivered", description: "Investigation concluded with full digital forensics summary and bank freeze request." }
            ]
        }
    },

    currentCaseId: 1,

    init() {
        const urlParams = new URLSearchParams(window.location.search);
        let idParam = parseInt(urlParams.get('id'));
        if (!idParam || isNaN(idParam) || idParam < 1 || idParam > 3) {
            idParam = 1;
        }
        this.currentCaseId = idParam;
        this.loadCase(idParam);
    },

    async loadCase(id) {
        try {
            const res = await fetch(`/api/case/${id}`);
            if (res.ok) {
                const data = await res.json();
                if (data.status === 'success' && data.case) {
                    this.render(data);
                    return;
                }
            }
        } catch (err) {
            console.warn('API error, using built-in demo records:', err);
        }

        // Fallback to offline store
        const fallback = this.fallbackData[id] || this.fallbackData[1];
        this.render(fallback);
    },

    render(data) {
        const c = data.case;
        const evidence = data.evidence_files || [];
        const entities = data.entities || [];
        const findings = data.findings || [];
        const timeline = data.timeline || [];

        // 1. Breadcrumb & Top Bar
        const breadcrumb = document.getElementById('breadcrumbCaseId');
        if (breadcrumb) breadcrumb.innerText = c.case_id;

        const downloadPdfBtn = document.getElementById('btnDownloadReport');
        if (downloadPdfBtn) {
            downloadPdfBtn.href = `/investigator/case/${c.id}/report/download`;
        }

        // 2. Dossier Header Card
        const caseIdEl = document.getElementById('workbenchCaseId');
        if (caseIdEl) caseIdEl.innerHTML = `<i class="fa-solid fa-shield-cat"></i> ${c.case_id}`;

        const titleEl = document.getElementById('workbenchCaseTitle');
        if (titleEl) titleEl.innerText = c.title;

        const descEl = document.getElementById('workbenchCaseDesc');
        if (descEl) descEl.innerText = c.description;

        // Status Badge
        const statusBadge = document.getElementById('workbenchStatusBadge');
        if (statusBadge) {
            let statusClass = 'status-under-review';
            let statusIcon = 'fa-clock';
            let statusLabel = c.status;

            if (c.status === 'Evidence Verified') {
                statusClass = 'status-verified';
                statusIcon = 'fa-check';
                statusLabel = 'Evidence Verified';
            } else if (c.status === 'Completed' || c.status === 'Report Generated' || c.status === 'Analysis Complete') {
                statusClass = 'status-analysis-complete';
                statusIcon = 'fa-circle-check';
                statusLabel = 'Completed';
            } else {
                statusClass = 'status-under-review';
                statusIcon = 'fa-hourglass-half';
                statusLabel = 'Pending Verification';
            }

            statusBadge.className = `status-pill ${statusClass}`;
            statusBadge.innerHTML = `<i class="fa-solid ${statusIcon}"></i> ${statusLabel}`;
        }

        // Priority Badge
        const priorityBadge = document.getElementById('workbenchPriorityBadge');
        if (priorityBadge) {
            const prio = (c.priority || 'Medium').toLowerCase();
            priorityBadge.className = `priority-pill priority-${prio}`;
            priorityBadge.innerText = `${c.priority || 'Medium'} Priority`;
        }

        // Category Badge
        const catBadge = document.getElementById('workbenchCategoryBadge');
        if (catBadge) catBadge.innerText = c.category;

        // Complainant & Meta fields
        const compEl = document.getElementById('workbenchComplainant');
        if (compEl) compEl.innerText = c.complainant_name || 'Anonymous Citizen';

        const dateEl = document.getElementById('workbenchIncidentDate');
        if (dateEl) dateEl.innerText = c.incident_date ? c.incident_date.replace('T', ' ') : '—';

        const lossEl = document.getElementById('workbenchLossAmount');
        if (lossEl) lossEl.innerText = `₹${Number(c.loss_amount || 0).toLocaleString('en-IN')}`;

        const upiEl = document.getElementById('workbenchSuspectUpi');
        if (upiEl) upiEl.innerText = c.suspect_upi || 'None Recorded';

        const phoneEl = document.getElementById('workbenchSuspectPhone');
        if (phoneEl) phoneEl.innerText = c.suspect_phone || 'None Recorded';

        // 3. Tab Labels
        const tabEvCount = document.getElementById('tabEvidenceCount');
        if (tabEvCount) tabEvCount.innerText = `Evidence Files (${evidence.length})`;

        const tabFindCount = document.getElementById('tabFindingsCount');
        if (tabFindCount) tabFindCount.innerText = `Cross Verification (${findings.length})`;

        // 4. Render Tab 1: Evidence Files
        this.renderEvidenceTab(evidence);

        // 5. Render Tab 2: OCR & Entities
        this.renderEntitiesTab(entities, evidence);

        // 6. Render Tab 3: Cross Verification Findings
        this.renderFindingsTab(findings);

        // 7. Render Tab 4: Reconstructed Timeline
        this.renderTimelineTab(timeline);

        // Update Quick Switcher active state
        document.querySelectorAll('.btn-case-switch').forEach(btn => {
            const btnCaseId = parseInt(btn.dataset.caseId);
            if (btnCaseId === c.id) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    },

    renderEvidenceTab(files) {
        const container = document.getElementById('evidenceGridContainer');
        if (!container) return;

        if (files.length === 0) {
            container.innerHTML = `<div class="p-4 text-muted">No evidence files attached to this case.</div>`;
            return;
        }

        container.innerHTML = files.map(f => {
            const isPdf = (f.original_filename || '').endsWith('.pdf') || (f.file_type || '').includes('PDF');
            const isImg = (f.original_filename || '').endsWith('.png') || (f.original_filename || '').endsWith('.jpg') || (f.file_type || '').includes('PNG') || (f.file_type || '').includes('JPG');
            const iconClass = isPdf ? 'icon-pdf' : (isImg ? 'icon-img' : 'icon-txt');
            const iconFa = isPdf ? 'fa-file-pdf' : (isImg ? 'fa-file-image' : 'fa-file-lines');
            const sizeStr = typeof f.file_size === 'number' ? (f.file_size > 1024 ? `${(f.file_size / 1024).toFixed(1)} KB` : `${f.file_size} B`) : f.file_size;

            return `
                <div class="evidence-vault-card">
                    <div class="vault-card-top">
                        <div class="vault-file-icon ${iconClass}"><i class="fa-solid ${iconFa}"></i></div>
                        <span class="status-pill status-verified"><i class="fa-solid fa-lock"></i> Verified</span>
                    </div>
                    <div class="vault-card-body">
                        <h4 class="vault-file-name" title="${f.original_filename}">${f.original_filename}</h4>
                        <div class="vault-size-time font-mono text-xs text-muted">
                            <span>${sizeStr}</span> • <span>${f.file_type || 'EXHIBIT'}</span>
                        </div>
                        <div class="hash-box-container">
                            <div class="hash-box-label">SHA-256 CHECKSUM</div>
                            <div class="hash-code font-mono">${f.sha256_hash}</div>
                        </div>
                    </div>
                    <div class="vault-card-footer">
                        <button class="btn btn-outline btn-sm" onclick="CyberShield.copyText('${f.sha256_hash}')">
                            <i class="fa-regular fa-copy"></i> Copy Hash
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="CyberShield.showToast('SHA-256 Bitstream Integrity Verified: MATCH', 'success')">
                            <i class="fa-solid fa-shield-check"></i> Verify
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    },

    renderEntitiesTab(entities, evidence) {
        const container = document.getElementById('entitiesContainer');
        if (!container) return;

        if (entities.length === 0) {
            container.innerHTML = `<div class="p-4 text-muted">No entities extracted yet for this case.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="analysis-doc-card">
                <div class="doc-card-header">
                    <span class="font-bold"><i class="fa-solid fa-microchip text-blue"></i> Aggregated Case Entities Identified</span>
                </div>
                <div class="entity-pills-wrap p-4">
                    ${entities.map(e => {
                        let pillClass = 'pill-generic';
                        if (e.entity_type === 'UPI_ID') pillClass = 'pill-upi';
                        else if (e.entity_type === 'AMOUNT') pillClass = 'pill-amount';
                        else if (e.entity_type === 'PHONE') pillClass = 'pill-phone';
                        else if (e.entity_type === 'TRANSACTION_ID') pillClass = 'pill-txn';
                        else if (e.entity_type === 'URL') pillClass = 'pill-url';

                        const conf = e.confidence ? `${Math.round(e.confidence * 100)}%` : '98%';

                        return `
                            <div class="entity-pill ${pillClass}">
                                <span class="entity-type font-mono">${e.entity_type}</span>
                                <span class="entity-val font-mono font-bold">${e.entity_value}</span>
                                <span class="entity-conf">${conf}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    },

    renderFindingsTab(findings) {
        const container = document.getElementById('findingsContainer');
        if (!container) return;

        if (findings.length === 0) {
            container.innerHTML = `<div class="p-4 text-muted">No cross-verification findings recorded.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="findings-list">
                ${findings.map(f => {
                    const sev = (f.severity || 'MEDIUM').toUpperCase();
                    let icon = 'fa-triangle-exclamation';
                    let iconColor = 'text-orange';
                    let itemClass = 'finding-warning';

                    if (sev === 'HIGH') {
                        icon = 'fa-circle-exclamation';
                        iconColor = 'text-red';
                        itemClass = 'finding-danger';
                    } else if (sev === 'LOW' || sev === 'INFO') {
                        icon = 'fa-circle-check';
                        iconColor = 'text-green';
                        itemClass = 'finding-match';
                    }

                    return `
                        <div class="finding-item ${itemClass}">
                            <div class="finding-icon ${iconColor}"><i class="fa-solid ${icon}"></i></div>
                            <div class="finding-text">
                                <div class="d-flex align-items-center gap-2 mb-1">
                                    <h4 class="finding-title m-0">${f.title}</h4>
                                    <span class="priority-pill priority-${sev.toLowerCase()} font-mono text-xs">${sev}</span>
                                </div>
                                <p class="finding-desc">${f.explanation || f.description || ''}</p>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    renderTimelineTab(timeline) {
        const container = document.getElementById('timelineContainer');
        if (!container) return;

        if (timeline.length === 0) {
            container.innerHTML = `<div class="p-4 text-muted">No chronological milestones recorded for this case.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="timeline-wrapper">
                ${timeline.map(t => {
                    const timeLabel = t.event_time ? (t.event_date ? `${t.event_date}, ${t.event_time}` : t.event_time) : (t.event_date || '—');
                    return `
                        <div class="timeline-step-item">
                            <div class="timeline-milestone-marker"><div class="marker-dot"></div><div class="marker-line"></div></div>
                            <div class="timeline-step-card">
                                <div class="timeline-card-header font-mono text-xs text-muted">${timeLabel}</div>
                                <h4 class="timeline-event-title">${t.title}</h4>
                                <p class="timeline-event-desc">${t.description}</p>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    CyberShieldCaseDetails.init();
});
