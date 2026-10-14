// ==========================================================================
// CyberShield — Evidence Relationship Graph (Cytoscape.js)
// ==========================================================================

const CyberShieldGraph = {
    cy: null,

    demoGraphData: {
        nodes: [
            // Case Core
            { data: { id: 'case_1', label: 'CS-2026-10492\n(OLX Advance Fraud)', type: 'case', color: '#1e3a8a' } },

            // Evidence Files
            { data: { id: 'file_1', label: 'GPay_Debit_Slip.png', type: 'evidence', color: '#2563eb' } },
            { data: { id: 'file_2', label: 'Bank_Statement.pdf', type: 'evidence', color: '#2563eb' } },
            { data: { id: 'file_3', label: 'WhatsApp_Chat.txt', type: 'evidence', color: '#2563eb' } },

            // Extracted Entities
            { data: { id: 'ent_upi_1', label: 'fake_merchant_scam@okaxis\n(UPI ID)', type: 'upi', color: '#ea580c' } },
            { data: { id: 'ent_phone_1', label: '+91 98765 43210\n(Phone)', type: 'phone', color: '#16a34a' } },
            { data: { id: 'ent_txn_1', label: 'UTR: 428901928401\n(Txn Ref)', type: 'txn', color: '#9333ea' } },
            { data: { id: 'ent_amt_1', label: '₹25,000.00\n(Amount)', type: 'amount', color: '#d97706' } },

            // Events
            { data: { id: 'evt_1', label: '09 Oct 15:45\nContact via WhatsApp', type: 'event', color: '#0284c7' } },
            { data: { id: 'evt_2', label: '09 Oct 16:15\nGPay Transfer Executed', type: 'event', color: '#0284c7' } }
        ],
        edges: [
            // Case to Evidence
            { data: { source: 'case_1', target: 'file_1', label: 'contains' } },
            { data: { source: 'case_1', target: 'file_2', label: 'contains' } },
            { data: { source: 'case_1', target: 'file_3', label: 'contains' } },

            // Files to Entities
            { data: { source: 'file_1', target: 'ent_upi_1', label: 'extracts' } },
            { data: { source: 'file_1', target: 'ent_amt_1', label: 'extracts' } },
            { data: { source: 'file_1', target: 'ent_txn_1', label: 'extracts' } },

            { data: { source: 'file_2', target: 'ent_upi_1', label: 'corroborates' } },
            { data: { source: 'file_2', target: 'ent_amt_1', label: 'corroborates' } },
            { data: { source: 'file_2', target: 'ent_txn_1', label: 'corroborates' } },

            { data: { source: 'file_3', target: 'ent_upi_1', label: 'solicits' } },
            { data: { source: 'file_3', target: 'ent_phone_1', label: 'communicates' } },

            // Entities to Events
            { data: { source: 'ent_phone_1', target: 'evt_1', label: 'involved_in' } },
            { data: { source: 'ent_txn_1', target: 'evt_2', label: 'settled_in' } }
        ]
    },

    init() {
        this.initCytoscape();
        this.bindControls();
    },

    initCytoscape() {
        const container = document.getElementById('cyCanvas');
        if (!container || typeof cytoscape === 'undefined') return;

        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

        this.cy = cytoscape({
            container: container,
            elements: this.demoGraphData,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': 'data(color)',
                        'label': 'data(label)',
                        'color': isDark ? '#f8fafc' : '#0f172a',
                        'font-size': '11px',
                        'font-family': 'DM Sans, sans-serif',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'text-wrap': 'wrap',
                        'text-max-width': '120px',
                        'width': 65,
                        'height': 65,
                        'border-width': 2,
                        'border-color': '#ffffff',
                        'text-outline-width': 2,
                        'text-outline-color': isDark ? '#090f1d' : '#ffffff'
                    }
                },
                {
                    selector: 'node[type="case"]',
                    style: {
                        'width': 90,
                        'height': 90,
                        'font-size': '12px',
                        'font-weight': 'bold',
                        'shape': 'hexagon'
                    }
                },
                {
                    selector: 'node[type="upi"]',
                    style: { 'shape': 'diamond', 'width': 75, 'height': 75 }
                },
                {
                    selector: 'node[type="phone"]',
                    style: { 'shape': 'round-rectangle', 'width': 80, 'height': 50 }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': isDark ? '#334155' : '#cbd5e1',
                        'target-arrow-color': isDark ? '#475569' : '#94a3b8',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '9px',
                        'color': isDark ? '#94a3b8' : '#64748b',
                        'text-rotation': 'autorotate',
                        'text-background-opacity': 1,
                        'text-background-color': isDark ? '#0c1324' : '#ffffff',
                        'text-background-padding': '3px'
                    }
                },
                {
                    selector: ':selected',
                    style: {
                        'border-width': 4,
                        'border-color': '#ea580c',
                        'line-color': '#ea580c',
                        'target-arrow-color': '#ea580c'
                    }
                }
            ],
            layout: {
                name: 'cose',
                animate: true,
                padding: 40
            }
        });

        // Click handler for node inspection
        this.cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            this.showNodeDetails(node.data());
        });

        this.cy.on('tap', (evt) => {
            if (evt.target === this.cy) {
                const inspector = document.getElementById('graphInspector');
                if (inspector) inspector.classList.remove('active');
            }
        });
    },

    showNodeDetails(data) {
        const inspector = document.getElementById('graphInspector');
        if (!inspector) return;

        document.getElementById('inspectorTitle').innerText = data.label.replace('\n', ' ');
        document.getElementById('inspectorType').innerText = data.type.toUpperCase();
        document.getElementById('inspectorId').innerText = data.id;

        inspector.classList.add('active');
    },

    setLayout(name) {
        if (!this.cy) return;
        this.cy.layout({ name: name, animate: true, padding: 40 }).run();
    },

    zoomIn() {
        if (!this.cy) return;
        this.cy.zoom(this.cy.zoom() * 1.25);
    },

    zoomOut() {
        if (!this.cy) return;
        this.cy.zoom(this.cy.zoom() * 0.8);
    },

    fit() {
        if (!this.cy) return;
        this.cy.fit(null, 40);
    },

    bindControls() {
        // Layout change buttons
        document.querySelectorAll('.graph-layout-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.graph-layout-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.setLayout(btn.dataset.layout);
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    CyberShieldGraph.init();
});
