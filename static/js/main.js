// CyberShield AI — Main Frontend Utilities

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips if any
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(el) {
        return new bootstrap.Tooltip(el);
    });

    // Auto-dismiss alerts after 6 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert.alert-dismissible');
        alerts.forEach(function(alert) {
            const bsAlert = bootstrap.Alert.getInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        });
    }, 6000);
});

// Copy text / hash to clipboard with visual feedback
function copyToClipboard(text, btnElement) {
    if (!navigator.clipboard) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showCopiedFeedback(btnElement);
        return;
    }
    navigator.clipboard.writeText(text).then(function() {
        showCopiedFeedback(btnElement);
    }).catch(function(err) {
        console.error('Copy failed:', err);
    });
}

function showCopiedFeedback(btn) {
    if (!btn) return;
    const origHtml = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copied';
    btn.classList.add('btn-success');
    setTimeout(function() {
        btn.innerHTML = origHtml;
        btn.classList.remove('btn-success');
    }, 1800);
}

// Live SHA-256 Verification Modal Fetcher
function triggerLiveHashVerify(evidenceId, filename) {
    const modalEl = document.getElementById('verifyHashModal');
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    
    document.getElementById('verifyModalFileName').innerText = filename;
    document.getElementById('verifyModalStatus').innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Calculating real-time SHA-256 cryptographic digest from disk...</p>
        </div>
    `;
    modal.show();

    fetch(`/api/evidence/${evidenceId}/verify`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            const isMatch = data.matched;
            document.getElementById('verifyModalStatus').innerHTML = `
                <div class="alert ${isMatch ? 'alert-success' : 'alert-danger'} mb-3">
                    <h6 class="alert-heading fw-bold mb-1">
                        <i class="bi ${isMatch ? 'bi-shield-check' : 'bi-shield-exclamation'} me-1"></i>
                        ${isMatch ? 'INTEGRITY VERIFIED: BIT-PERFECT MATCH' : 'ALERT: INTEGRITY MISMATCH DETECTED'}
                    </h6>
                    <small>${data.message}</small>
                </div>
                <div class="bg-dark p-3 rounded mb-2 border border-secondary">
                    <div class="mb-2">
                        <span class="text-muted small d-block">Recorded Hash (At Intake):</span>
                        <code class="text-info font-monospace small">${data.recorded_hash || 'None'}</code>
                    </div>
                    <div>
                        <span class="text-muted small d-block">Current Hash (Calculated on Disk):</span>
                        <code class="${isMatch ? 'text-success' : 'text-danger'} font-monospace small">${data.current_hash || 'Unreadable'}</code>
                    </div>
                </div>
                <div class="small text-muted mt-2">
                    <i class="bi bi-info-circle me-1"></i>
                    CyberShield verified that original bytes on storage have not been altered or corrupted.
                </div>
            `;
        })
        .catch(err => {
            document.getElementById('verifyModalStatus').innerHTML = `
                <div class="alert alert-danger">Error communicating with verification endpoint: ${err}</div>
            `;
        });
}

// Re-run AI & Rule analysis via AJAX
function rerunAnalysis(caseId, btn) {
    if (!confirm('Re-run full OCR text extraction, entity recognition, and cross-evidence verification rules on this case?')) {
        return;
    }
    const origHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing Pipeline...';

    fetch(`/api/case/${caseId}/analyze`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            btn.innerHTML = origHtml;
            btn.disabled = false;
            if (data.status === 'success') {
                alert(`Analysis complete! ${data.message}`);
                window.location.reload();
            } else {
                alert('Analysis error: ' + data.message);
            }
        })
        .catch(err => {
            btn.innerHTML = origHtml;
            btn.disabled = false;
            alert('Request error: ' + err);
        });
}
