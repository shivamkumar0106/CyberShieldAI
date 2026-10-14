// CyberShield AI — Cytoscape.js Relationship Graph Controller

let cy = null;
let currentCaseId = null;

function initRelationshipGraph(caseId) {
    currentCaseId = caseId;
    const container = document.getElementById('cy-container');
    if (!container) return;

    fetch(`/api/case/${caseId}/graph`)
        .then(res => res.json())
        .then(data => {
            renderCytoscape(data);
        })
        .catch(err => {
            console.error('Failed to load graph data:', err);
            container.innerHTML = `
                <div class="d-flex align-items-center justify-content-center h-100 text-muted">
                    <div><i class="bi bi-exclamation-triangle text-warning fs-3 mb-2"></i><br/>Unable to load relationship graph data.</div>
                </div>
            `;
        });
}

function renderCytoscape(graphData) {
    const container = document.getElementById('cy-container');
    if (!container) return;

    // Update stats pills
    if (graphData.stats) {
        const statsEl = document.getElementById('graphStatsText');
        if (statsEl) {
            statsEl.innerText = `${graphData.stats.total_nodes} Nodes, ${graphData.stats.total_edges} Connections across ${graphData.stats.unique_entities} Extracted Entities`;
        }
    }

    cy = cytoscape({
        container: container,
        elements: graphData.elements,
        style: [
            // Generic Node
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'color': '#0f172a',
                    'font-size': '11px',
                    'font-weight': '600',
                    'text-valign': 'bottom',
                    'text-margin-y': 6,
                    'background-color': 'data(color)',
                    'width': 'data(size)',
                    'height': 'data(size)',
                    'border-width': 2,
                    'border-color': '#ffffff',
                    'border-opacity': 0.9,
                    'text-outline-color': '#ffffff',
                    'text-outline-width': 3,
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.3s'
                }
            },
            // Shared Entities (High value correlation hubs)
            {
                selector: 'node[?is_shared]',
                style: {
                    'border-width': 4,
                    'border-color': '#f59e0b',
                    'border-opacity': 1.0,
                    'shadow-blur': 12,
                    'shadow-color': '#f59e0b',
                    'shadow-opacity': 0.4
                }
            },
            // Case Root Node
            {
                selector: 'node[type="case"]',
                style: {
                    'shape': 'diamond',
                    'border-width': 3,
                    'border-color': '#2563eb'
                }
            },
            // File Nodes
            {
                selector: 'node[type="file"]',
                style: {
                    'shape': 'round-rectangle',
                    'border-width': 2,
                    'border-color': '#0284c7'
                }
            },
            // Timeline Event Nodes
            {
                selector: 'node[type="event"]',
                style: {
                    'shape': 'hexagon',
                    'border-width': 2,
                    'border-color': '#ea580c'
                }
            },
            // Edges
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': 'data(line_color)',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'target-arrow-color': 'data(line_color)',
                    'arrow-scale': 1.0,
                    'opacity': 0.7,
                    'label': 'data(label)',
                    'font-size': '9px',
                    'font-weight': '500',
                    'color': '#475569',
                    'text-background-opacity': 0.9,
                    'text-background-color': '#ffffff',
                    'text-background-padding': 2,
                    'text-background-shape': 'roundrectangle'
                }
            },
            // Selected Node
            {
                selector: ':selected',
                style: {
                    'border-width': 4,
                    'border-color': '#0f172a',
                    'shadow-blur': 20,
                    'shadow-color': '#2563eb',
                    'shadow-opacity': 0.6
                }
            }
        ],
        layout: {
            name: 'cose',
            animate: false,
            idealEdgeLength: 100,
            nodeOverlap: 20,
            refresh: 20,
            fit: true,
            padding: 40,
            componentSpacing: 100
        }
    });

    // Node Click Listener -> Update Inspector
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        showNodeDetails(node.data());
    });

    // Background Click -> Reset Inspector
    cy.on('tap', function(evt) {
        if (evt.target === cy) {
            resetInspector();
        }
    });
}

function showNodeDetails(data) {
    const inspector = document.getElementById('graphInspector');
    if (!inspector) return;

    inspector.style.display = 'block';
    let html = `
        <div class="d-flex justify-content-between align-items-center mb-2 border-bottom pb-2">
            <span class="badge" style="background-color: ${data.color}; color: #ffffff;">${data.category || data.type.toUpperCase()}</span>
            <button class="btn btn-sm btn-light py-0 px-2" onclick="resetInspector()">&times;</button>
        </div>
        <h6 class="text-dark fw-bold mb-2">${data.full_value || data.full_name || data.full_title || data.label}</h6>
    `;

    if (data.is_shared) {
        html += `
            <div class="alert alert-warning py-1 px-2 small mb-2 border-0 bg-warning bg-opacity-25 text-warning-emphasis">
                <i class="bi bi-link-45deg me-1"></i> <b>Shared Identifier:</b> In ${data.shared_count} independent files.
            </div>
        `;
    }

    if (data.details) {
        html += '<table class="table table-sm small mb-0">';
        for (const [key, val] of Object.entries(data.details)) {
            let displayVal = val;
            if (Array.isArray(val)) {
                displayVal = val.join(', ');
            }
            const cleanKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            html += `
                <tr>
                    <td class="text-muted text-nowrap py-1" style="width:35%;">${cleanKey}:</td>
                    <td class="text-break text-dark fw-medium py-1">${displayVal}</td>
                </tr>
            `;
        }
        html += '</table>';
    }

    inspector.innerHTML = html;
}

function resetInspector() {
    const inspector = document.getElementById('graphInspector');
    if (!inspector) return;
    inspector.innerHTML = `
        <div class="text-center text-muted py-4">
            <i class="bi bi-hand-index-thumb fs-4 d-block mb-1 text-primary"></i>
            <small>Click any node or relationship link to inspect extracted attributes and forensic references.</small>
        </div>
    `;
}

// Layout Switcher
function changeGraphLayout(layoutName) {
    if (!cy) return;
    cy.layout({
        name: layoutName,
        animate: true,
        animationDuration: 500,
        fit: true,
        padding: 40
    }).run();
}

function zoomInGraph() {
    if (cy) cy.zoom(cy.zoom() * 1.25);
}

function zoomOutGraph() {
    if (cy) cy.zoom(cy.zoom() * 0.8);
}

function resetGraphView() {
    if (cy) {
        cy.fit();
        cy.center();
    }
}
