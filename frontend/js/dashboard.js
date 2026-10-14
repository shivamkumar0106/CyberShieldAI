// ==========================================================================
// CyberShield — Dashboard Controller
// ==========================================================================

const CyberShieldDashboard = {
    demoCases: [
        {
            id: 1,
            case_id: "CS-2026-28410",
            title: "Telegram VIP Crypto Doubling & Task Scheme Fraud",
            category: "Financial Fraud",
            complainant_name: "Sneha Reddy",
            incident_date: "2026-10-07",
            loss_amount: 75000,
            status: "Under Review",
            priority: "High",
            evidence_count: 2,
            high_flags: 1
        },
        {
            id: 2,
            case_id: "CS-2026-10492",
            title: "OLX Camera Advance Payment Scam & Fake GPay Slip",
            category: "Online Payment Fraud",
            complainant_name: "Aarav Patel",
            incident_date: "2026-10-09",
            loss_amount: 25000,
            status: "Evidence Verified",
            priority: "High",
            evidence_count: 3,
            high_flags: 1
        },
        {
            id: 3,
            case_id: "CS-2026-39148",
            title: "Bank KYC Phishing SMS & Unauthorized IMPS Transfer",
            category: "Phishing & Identity Theft",
            complainant_name: "Rajesh Kumar",
            incident_date: "2026-10-05",
            loss_amount: 12000,
            status: "Completed",
            priority: "Medium",
            evidence_count: 2,
            high_flags: 1
        }
    ],

    init() {
        this.loadCases();
        this.bindEvents();
    },

    async loadCases() {
        const tableBody = document.getElementById('dashboardCasesTableBody');
        if (!tableBody) return;

        try {
            const res = await fetch('/api/cases');
            if (res.ok) {
                const data = await res.json();
                if (data.cases && data.cases.length > 0) {
                    this.renderCases(data.cases);
                    this.updateStats(data.stats || null);
                    return;
                }
            }
        } catch (e) {
            console.warn('API unavailable, rendering initialized local workspace records', e);
        }

        // Render demo data fallback
        this.renderCases(this.demoCases);
    },

    renderCases(cases) {
        const tableBody = document.getElementById('dashboardCasesTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = cases.map(c => `
            <tr>
                <td>
                    <a href="/pages/case-details.html?id=${c.id}" class="case-id-link">
                        <span class="font-mono font-bold">${c.case_id}</span>
                    </a>
                </td>
                <td>
                    <div class="case-title-cell">
                        <span class="font-bold text-dark">${c.title}</span>
                        <span class="text-muted text-xs">${c.complainant_name || 'Complainant'} • ${c.incident_date}</span>
                    </div>
                </td>
                <td>
                    <span class="category-pill">${c.category}</span>
                </td>
                <td class="font-mono text-dark">
                    ₹${Number(c.loss_amount || 0).toLocaleString('en-IN')}
                </td>
                <td>
                    <span class="status-pill status-${(c.status || '').toLowerCase().replace(/\s+/g, '-')}">
                        ${c.status}
                    </span>
                </td>
                <td>
                    <span class="badge-evidence-count">
                        <i class="fa-regular fa-file"></i> ${c.evidence_count || 1}
                    </span>
                </td>
                <td>
                    <div class="table-actions">
                        <a href="/pages/case-details.html?id=${c.id}" class="btn btn-outline btn-sm" title="Open Case Workbench">
                            <span>Open</span> <i class="fa-solid fa-arrow-right"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    updateStats(stats) {
        if (!stats) return;
        if (document.getElementById('kpiTotalCases')) document.getElementById('kpiTotalCases').innerText = stats.total_cases;
        if (document.getElementById('kpiEvidence')) document.getElementById('kpiEvidence').innerText = stats.total_evidence;
        if (document.getElementById('kpiPending')) document.getElementById('kpiPending').innerText = stats.pending_cases;
        if (document.getElementById('kpiHighAlerts')) document.getElementById('kpiHighAlerts').innerText = stats.high_findings;
    },

    bindEvents() {
        const searchInput = document.getElementById('caseSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                const rows = document.querySelectorAll('#dashboardCasesTableBody tr');
                rows.forEach(r => {
                    r.style.display = r.innerText.toLowerCase().includes(q) ? '' : 'none';
                });
            });
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    CyberShieldDashboard.init();
});
