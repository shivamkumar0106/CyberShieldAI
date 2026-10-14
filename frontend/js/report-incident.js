// ==========================================================================
// CyberShield — Report Incident & Evidence Intake Controller
// ==========================================================================

const CyberShieldIntake = {
    selectedFiles: [],

    init() {
        this.bindDropzone();
        this.checkCitizenAuth();
    },

    checkCitizenAuth() {
        const user = window.CyberShieldAuth ? CyberShieldAuth.getUser() : null;
        if (user && user.role === 'citizen') {
            const banner = document.getElementById('citizenIdentityBanner');
            if (banner) {
                banner.style.display = 'flex';
                if (document.getElementById('citizenNameText')) {
                    document.getElementById('citizenNameText').innerText = `Verified Citizen: ${user.full_name}`;
                }
                if (document.getElementById('citizenPhoneText')) {
                    document.getElementById('citizenPhoneText').innerText = `Mobile: ${user.phone || '+91 98223 34455'}`;
                }
            }
        }
    },

    bindDropzone() {
        const dropzone = document.getElementById('evidenceDropzone');
        const fileInput = document.getElementById('evidenceFileInput');
        const fileList = document.getElementById('selectedFilesList');

        if (!dropzone || !fileInput) return;

        dropzone.addEventListener('click', () => fileInput.click());

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                this.handleFiles(e.dataTransfer.files);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                this.handleFiles(fileInput.files);
            }
        });
    },

    async handleFiles(files) {
        const fileListContainer = document.getElementById('selectedFilesList');
        if (!fileListContainer) return;

        for (const file of Array.from(files)) {
            // Calculate instant client-side SHA-256 hash preview
            const hash = await this.calculateSha256(file);
            const fileItem = {
                file,
                name: file.name,
                size: (file.size / 1024).toFixed(1) + ' KB',
                type: file.type || 'Document',
                hash: hash
            };
            this.selectedFiles.push(fileItem);
        }

        this.renderFileList();
    },

    async calculateSha256(file) {
        try {
            const buffer = await file.arrayBuffer();
            const digest = await crypto.subtle.digest('SHA-256', buffer);
            const hashArray = Array.from(new Uint8Array(digest));
            return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        } catch (e) {
            return "sha256_calculated_upon_upload";
        }
    },

    renderFileList() {
        const container = document.getElementById('selectedFilesList');
        if (!container) return;

        if (this.selectedFiles.length === 0) {
            container.innerHTML = '';
            return;
        }

        container.innerHTML = `
            <div class="evidence-queue-header">
                <span class="font-bold">Attached Evidence (${this.selectedFiles.length} files)</span>
                <span class="text-xs text-muted">Cryptographic integrity recorded upon submission</span>
            </div>
            ${this.selectedFiles.map((item, idx) => `
                <div class="queue-item-card">
                    <div class="queue-item-icon">
                        <i class="fa-regular fa-file"></i>
                    </div>
                    <div class="queue-item-info">
                        <div class="queue-item-name font-bold">${item.name}</div>
                        <div class="queue-item-meta">${item.size} • ${item.type}</div>
                        <div class="queue-item-hash font-mono text-xs text-muted">
                            <span class="text-green"><i class="fa-solid fa-lock"></i> SHA-256:</span> ${item.hash}
                        </div>
                    </div>
                    <button type="button" class="queue-remove-btn" onclick="CyberShieldIntake.removeFile(${idx})">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
            `).join('')}
        `;
    },

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.renderFileList();
    }
};

document.addEventListener('DOMContentLoaded', () => {
    CyberShieldIntake.init();
});
