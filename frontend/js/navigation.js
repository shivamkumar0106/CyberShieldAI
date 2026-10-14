// ==========================================================================
// CyberShield — Navigation & Session Persistence Controller
// Synchronizes authentication state across all pages (Home, Dashboard, Vault, Intake)
// ==========================================================================

const CyberShieldAuth = {
    getUser() {
        try {
            const raw = localStorage.getItem('cs_user');
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    },

    setUser(user) {
        if (user) {
            localStorage.setItem('cs_user', JSON.stringify(user));
        } else {
            localStorage.removeItem('cs_user');
        }
        this.renderNavbarUser();
    },

    async checkSession() {
        // Immediate render from localStorage to prevent UI flicker
        this.renderNavbarUser();

        // Validate with server session
        try {
            const res = await fetch('/api/auth/me');
            if (res.ok) {
                const data = await res.json();
                if (data.authenticated && data.user) {
                    this.setUser(data.user);
                    this.enforceRoleAccess(data.user);
                } else {
                    // Not authenticated on server
                    if (this.getUser()) {
                        this.setUser(null);
                    }
                }
            }
        } catch (e) {
            console.log('Server session check deferred:', e);
        }
    },

    enforceRoleAccess(user) {
        const path = window.location.pathname;
        
        // If a CITIZEN enters investigator-only pages (dashboard, cases directory, vault), route them to intake
        if (user.role === 'citizen') {
            const investigatorPages = ['dashboard.html', 'cases.html', 'evidence-vault.html', 'evidence-graph.html'];
            const isInvestigatorPage = investigatorPages.some(p => path.includes(p));
            if (isInvestigatorPage) {
                if (window.CyberShield && window.CyberShield.showToast) {
                    CyberShield.showToast('Citizen Access: Opening your Incident Complaint form...', 'info');
                }
                setTimeout(() => {
                    window.location.href = '/pages/report-incident.html';
                }, 400);
            }
        }
    },

    renderNavbarUser() {
        const user = this.getUser();
        const navActions = document.querySelector('.nav-actions');
        if (!navActions) return;

        // Find existing login button or existing user pill
        const loginBtn = navActions.querySelector('a[href*="login"]');
        let userContainer = navActions.querySelector('.user-session-container');

        if (!user) {
            // Unauthenticated state: show Login button if missing
            if (userContainer) userContainer.remove();
            if (!loginBtn) {
                const newLoginBtn = document.createElement('a');
                newLoginBtn.href = '/pages/login.html';
                newLoginBtn.className = 'btn btn-primary';
                newLoginBtn.setAttribute('data-i18n', 'nav_login');
                newLoginBtn.innerText = 'Login';
                navActions.appendChild(newLoginBtn);
            }
            return;
        }

        // Authenticated state: Replace login button with User Profile Pill
        if (loginBtn) loginBtn.remove();
        if (!userContainer) {
            userContainer = document.createElement('div');
            userContainer.className = 'user-session-container';
            navActions.appendChild(userContainer);
        }

        const isCitizen = user.role === 'citizen';
        const roleLabel = isCitizen ? 'Citizen' : 'Investigator';
        const icon = isCitizen ? 'fa-user-shield text-blue' : 'fa-user-tie text-orange';
        const actionBtn = isCitizen
            ? `<a href="/pages/report-incident.html" class="btn btn-outline btn-sm" style="padding: 4px 10px; font-size: 0.76rem;">Report</a>`
            : `<a href="/pages/dashboard.html" class="btn btn-outline btn-sm" style="padding: 4px 10px; font-size: 0.76rem;">Dashboard</a>`;

        userContainer.innerHTML = `
            <div class="user-session-pill">
                <i class="fa-solid ${icon}"></i>
                <span class="user-pill-name font-bold">${user.full_name || user.username || 'User'}</span>
                <span class="role-tag-badge">${roleLabel}</span>
                ${actionBtn}
                <button type="button" onclick="CyberShieldAuth.logout(event)" class="logout-link" title="Sign Out">
                    <i class="fa-solid fa-power-off"></i>
                </button>
            </div>
        `;

        // Update citizen form complainant name if on report-incident page
        if (isCitizen && window.location.pathname.includes('report-incident.html')) {
            const descEl = document.getElementById('complainantNameHint');
            if (descEl) descEl.innerText = `Lodged by: ${user.full_name} (${user.phone || ''})`;
        }
    },

    async logout(e) {
        if (e) e.preventDefault();
        this.setUser(null);
        try {
            await fetch('/auth/logout');
        } catch (err) {}
        window.location.href = '/';
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Highlight active link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav-link, .nav-link-item');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && (currentPath.endsWith(href) || currentPath === href || (href !== '/' && currentPath.includes(href)))) {
            link.classList.add('active');
        }
    });

    // Check & persist session across all pages
    CyberShieldAuth.checkSession();
});

window.CyberShieldAuth = CyberShieldAuth;
