// ==========================================================================
// CyberShield — Cases Directory Controller
// ==========================================================================

const CyberShieldCases = {
    cases: [
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
            suspect_upi: "vip_crypto_admin@icici",
            suspect_phone: "+91 91234 56789",
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
            suspect_upi: "fake_merchant_scam@okaxis",
            suspect_phone: "+91 98765 43210",
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
            suspect_upi: "sbi_kyc_verify@upi",
            suspect_phone: "+91 98111 22334",
            evidence_count: 2,
            high_flags: 1
        }
    ],

    activeStatus: 'all',
    activeCategory: 'all',
    searchQuery: '',

    init() {
        this.fetchCases();
        this.bindEvents();
    },

    async fetchCases() {
        try {
            const res = await fetch('/api/cases');
            if (res.ok) {
                const data = await res.json();
                if (data.cases && data.cases.length > 0) {
                    this.cases = data.cases;
                }
            }
        } catch (e) {
            console.log('Using pre-populated directory records');
        }
        this.render();
    },

    bindEvents() {
        // Status filter tabs
        document.querySelectorAll('.status-filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.status-filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.activeStatus = btn.dataset.status;
                this.render();
            });
        });

        // Search input
        const searchInput = document.getElementById('casesSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase().trim();
                this.render();
            });
        }
    },

    render() {
        const container = document.getElementById('casesTableBody');
        if (!container) return;

        const filtered = this.cases.filter(c => {
            const matchStatus = this.activeStatus === 'all' || 
                c.status.toLowerCase().replace(/\s+/g, '-') === this.activeStatus.toLowerCase();
            
            const matchSearch = !this.searchQuery || 
                c.case_id.toLowerCase().includes(this.searchQuery) ||
                c.title.toLowerCase().includes(this.searchQuery) ||
                (c.complainant_name && c.complainant_name.toLowerCase().includes(this.searchQuery)) ||
                (c.suspect_upi && c.suspect_upi.toLowerCase().includes(this.searchQuery));

            return matchStatus && matchSearch;
        });

        document.getElementById('caseCountDisplay').innerText = `${filtered.length} Cases Found`;

        if (filtered.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-5 text-muted">
                        <i class="fa-solid fa-folder-open mb-2 text-2xl"></i>
                        <p>No investigation cases match the selected filter criteria.</p>
                    </td>
                </tr>
            `;
            return;
        }

        container.innerHTML = filtered.map(c => `
            <tr>
                <td>
                    <a href="/pages/case-details.html?id=${c.id}" class="case-id-link font-mono font-bold">
                        ${c.case_id}
                    </a>
                </td>
                <td>
                    <div class="case-title-cell">
                        <span class="font-bold text-dark">${c.title}</span>
                        <span class="text-muted text-xs">Complainant: ${c.complainant_name || 'Citizen'} • ${c.incident_date}</span>
                    </div>
                </td>
                <td>
                    <span class="category-pill">${c.category}</span>
                </td>
                <td class="font-mono text-dark font-semibold">
                    ₹${Number(c.loss_amount || 0).toLocaleString('en-IN')}
                </td>
                <td>
                    <span class="status-pill status-${(c.status || '').toLowerCase().replace(/\s+/g, '-')}">
                        ${c.status}
                    </span>
                </td>
                <td>
                    <span class="badge-evidence-count">
                        <i class="fa-regular fa-file"></i> ${c.evidence_count || 1} file(s)
                    </span>
                </td>
                <td>
                    <a href="/pages/case-details.html?id=${c.id}" class="btn btn-outline btn-sm">
                        <span>Workbench</span> <i class="fa-solid fa-arrow-right"></i>
                    </a>
                </td>
            </tr>
        `).join('');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    CyberShieldCases.init();
});
