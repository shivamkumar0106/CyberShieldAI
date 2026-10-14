// ==========================================================================
// CyberShield — Global Core Script
// Typography: Manrope (Headings), DM Sans (Body/Forms), JetBrains Mono (Tech/IDs)
// ==========================================================================

const CyberShieldI18n = {
    en: {
        nav_home: "Home",
        nav_features: "Features",
        nav_how_it_works: "How It Works",
        nav_cases: "Cases",
        nav_dashboard: "Dashboard",
        nav_login: "Login",
        nav_report: "Report Incident",
        nav_track: "Track Report",
        nav_evidence: "Evidence Vault",
        nav_analysis: "Analysis Results",
        nav_timeline: "Incident Timeline",
        nav_graph: "Evidence Graph",

        hero_pill: "CYBERCRIME INVESTIGATION SUPPORT PLATFORM",
        hero_title_1: "Turning Digital Evidence into",
        hero_title_2: "Real Justice",
        hero_desc: "CyberShield helps citizens report cybercrimes and assists investigators in collecting, analyzing and visualizing digital evidence from images, documents and metadata — faster, smarter and more securely.",
        hero_btn_report: "Report an Incident",
        hero_btn_track: "Track Report",
        val_secure: "Secure",
        val_efficient: "Efficient",
        val_friendly: "Citizen Friendly",
        val_support: "Investigation Support",

        visual_hub_title: "Digital Evidence",
        visual_hub_sub: "COLLECT · VERIFY · CONNECT",
        visual_phishing_title: "Phishing message",
        visual_phishing_sub: "Suspicious link detected",
        visual_doc_title: "Evidence document",
        visual_doc_sub: "Text extraction available",
        visual_meta_title: "Image metadata",
        visual_meta_sub: "Timestamp and properties",
        visual_rel_title: "Related identifier",
        visual_rel_sub: "Potential connection found",
        visual_pill_timeline: "Event timeline",
        visual_pill_integrity: "Evidence integrity",

        feat_1_title: "Report & Upload Evidence",
        feat_1_desc: "Submit cybercrime complaints with images, documents and details.",
        feat_2_title: "Automatic Evidence Analysis",
        feat_2_desc: "Extract text, metadata and key information using OCR and NLP.",
        feat_3_title: "Visualize Connections",
        feat_3_desc: "Interactive timelines and relationship graphs to uncover important links.",
        feat_4_title: "Support Investigations",
        feat_4_desc: "Organized evidence, consistency checks and downloadable reports for investigators.",

        stat_cases_num: "550+",
        stat_cases_label: "Cases Reported",
        stat_progress_num: "156",
        stat_progress_label: "In Progress",
        stat_solved_num: "360",
        stat_solved_label: "Cases Solved",

        how_title: "How CyberShield Works",
        how_sub: "A clear workflow from complaint intake to structured investigation support.",
        step_1_title: "Report Incident",
        step_1_desc: "Provide details and upload your available evidence.",
        step_2_title: "Analyze Evidence",
        step_2_desc: "Extract text, metadata and key entities automatically.",
        step_3_title: "View Insights",
        step_3_desc: "Review timelines, graphs and consistency checks.",
        step_4_title: "Generate Report",
        step_4_desc: "Download a structured investigation summary.",

        clarity_tag: "BUILT FOR CLARITY",
        clarity_head_1: "Evidence organized.",
        clarity_head_2: "Investigations supported.",
        clarity_desc: "CyberShield brings complaint details and digital evidence into one structured workflow. Automated results assist human review; they do not replace professional judgment.",
        clarity_btn: "Explore the workflow",

        cta_tag: "GET STARTED",
        cta_head: "Make digital evidence easier to review.",
        cta_desc: "Explore the prototype workflow and see how the platform organizes case information.",
        cta_btn: "Report an Incident",

        footer_notice: "CyberShield is a prototype investigation-support platform, not an official government reporting portal."
    },
    hi: {
        nav_home: "होम",
        nav_features: "विशेषताएं",
        nav_how_it_works: "प्रक्रिया",
        nav_cases: "मामले",
        nav_dashboard: "डैशबोर्ड",
        nav_login: "लॉग इन",
        nav_report: "शिकायत दर्ज करें",
        nav_track: "रिपोर्ट ट्रैक करें",
        nav_evidence: "साक्ष्य वॉल्ट",
        nav_analysis: "विश्लेषण",
        nav_timeline: "घटनाक्रम",
        nav_graph: "साक्ष्य आरेख",

        hero_pill: "साइबर अपराध डिजिटल जांच सहायता मंच",
        hero_title_1: "डिजिटल साक्ष्यों को",
        hero_title_2: "सच्चे न्याय में बदलना",
        hero_desc: "साइबरशील्ड नागरिकों को साइबर अपराधों की रिपोर्ट करने और जांचकर्ताओं को छवियों, दस्तावेजों और मेटाडेटा से डिजिटल साक्ष्य निकालने, जांचने और विज़ुअलाइज़ करने में मदद करता है — सुरक्षित, तेज़ और पारदर्शी।",
        hero_btn_report: "घटना की रिपोर्ट करें",
        hero_btn_track: "रिपोर्ट ट्रैक करें",
        val_secure: "सुरक्षित",
        val_efficient: "कुशल",
        val_friendly: "नागरिक अनुकूल",
        val_support: "जांच सहायता",

        visual_hub_title: "डिजिटल साक्ष्य",
        visual_hub_sub: "एकत्रित · सत्यापित · संबंधित",
        visual_phishing_title: "फ़िशिंग संदेश",
        visual_phishing_sub: "संदिग्ध लिंक पाया गया",
        visual_doc_title: "साक्ष्य दस्तावेज़",
        visual_doc_sub: "टेक्स्ट निष्कर्षण उपलब्ध",
        visual_meta_title: "छवि मेटाडेटा",
        visual_meta_sub: "समय-मुहर और गुण",
        visual_rel_title: "संबंधित पहचानकर्ता",
        visual_rel_sub: "संभावित संबंध मिला",
        visual_pill_timeline: "घटना समयरेखा",
        visual_pill_integrity: "साक्ष्य अखंडता",

        feat_1_title: "साक्ष्य अपलोड व रिपोर्टिंग",
        feat_1_desc: "छवियों, दस्तावेजों और विवरण के साथ साइबर अपराध की शिकायतें दर्ज करें।",
        feat_2_title: "स्वचालित साक्ष्य विश्लेषण",
        feat_2_desc: "OCR और भाषा विश्लेषण द्वारा टेक्स्ट, मेटाडेटा और मुख्य जानकारी निकालें।",
        feat_3_title: "संबंधों का दृश्य चित्रण",
        feat_3_desc: "महत्वपूर्ण लिंक उजागर करने के लिए संवादात्मक घटनाक्रम और संबंध आरेख।",
        feat_4_title: "जांच में सीधा सहयोग",
        feat_4_desc: "जांचकर्ताओं के लिए व्यवस्थित साक्ष्य, विसंगति परीक्षण और डाउनलोड रिपोर्ट।",

        stat_cases_num: "550+",
        stat_cases_label: "दर्ज मामले",
        stat_progress_num: "156",
        stat_progress_label: "प्रगति पर",
        stat_solved_num: "360",
        stat_solved_label: "सुलझाए गए मामले",

        how_title: "साइबरशील्ड कैसे कार्य करता है",
        how_sub: "शिकायत दर्ज करने से लेकर संरचित जांच सहायता तक एक स्पष्ट कार्यप्रवाह।",
        step_1_title: "1. घटना दर्ज करें",
        step_1_desc: "विवरण प्रदान करें और उपलब्ध साक्ष्य अपलोड करें।",
        step_2_title: "2. साक्ष्य विश्लेषण",
        step_2_desc: "टेक्स्ट, मेटाडेटा और संस्थाओं को स्वतः निकालें।",
        step_3_title: "3. अंतर्दृष्टि देखें",
        step_3_desc: "समयरेखा, आरेख और संगति परीक्षण देखें।",
        step_4_title: "4. रिपोर्ट तैयार करें",
        step_4_desc: "संरचित जांच सारांश रिपोर्ट डाउनलोड करें।",

        clarity_tag: "स्पष्टता के लिए निर्मित",
        clarity_head_1: "साक्ष्य संगठित।",
        clarity_head_2: "जांच में सहायता।",
        clarity_desc: "साइबरशील्ड शिकायत विवरण और डिजिटल साक्ष्य को एक व्यवस्थित कार्यप्रवाह में लाता है। स्वचालित परिणाम मानव समीक्षा का समर्थन करते हैं।",
        clarity_btn: "प्रक्रिया देखें",

        cta_tag: "शुरू करें",
        cta_head: "डिजिटल साक्ष्य की समीक्षा को आसान बनाएं।",
        cta_desc: "प्रोटोटाइप कार्यप्रवाह का अन्वेषण करें और देखें कि प्लेटफॉर्म मामले की जानकारी को कैसे व्यवस्थित करता है।",
        cta_btn: "घटना की रिपोर्ट करें",

        footer_notice: "साइबरशील्ड एक जांच-सहायता प्रोटोटाइप है, आधिकारिक सरकारी रिपोर्टिंग पोर्टल नहीं।"
    }
};

const CyberShield = {
    lang: localStorage.getItem('cs_lang') || 'en',
    theme: localStorage.getItem('cs_theme') || 'light',

    init() {
        this.applyTheme(this.theme);
        this.applyLanguage(this.lang);
        this.setupToastContainer();
        this.initButtonRipples();
        this.initStatsCounter();
    },

    initButtonRipples() {
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn');
            if (!btn) return;

            const rect = btn.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height) * 1.5;
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            const ripple = document.createElement('span');
            ripple.className = 'btn-click-ripple';
            ripple.style.width = `${size}px`;
            ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            btn.appendChild(ripple);
            setTimeout(() => {
                if (ripple.parentElement) ripple.remove();
            }, 650);
        });
    },

    parseCounterValue(rawString, explicitTarget, explicitSuffix, explicitPrefix) {
        if (explicitTarget !== null && explicitTarget !== undefined && String(explicitTarget).trim() !== '') {
            const cleanTargetStr = String(explicitTarget).trim();
            const hasCommas = cleanTargetStr.includes(',');
            const cleanNum = cleanTargetStr.replace(/,/g, '');
            const decimals = cleanNum.includes('.') ? cleanNum.split('.')[1].length : 0;
            const target = parseFloat(cleanNum) || 0;
            return {
                prefix: explicitPrefix || '',
                target: target,
                suffix: explicitSuffix !== null && explicitSuffix !== undefined ? String(explicitSuffix) : '',
                decimals: decimals,
                hasCommas: hasCommas
            };
        }

        const str = String(rawString || '').trim();
        const match = str.match(/^([^\d]*)([\d,]+(?:\.\d+)?)(.*)$/);
        if (!match) {
            return {
                prefix: '',
                target: 0,
                suffix: str,
                decimals: 0,
                hasCommas: false
            };
        }

        const prefix = explicitPrefix !== null && explicitPrefix !== undefined ? String(explicitPrefix) : match[1];
        const numPart = match[2];
        const suffix = explicitSuffix !== null && explicitSuffix !== undefined ? String(explicitSuffix) : match[3];
        const hasCommas = numPart.includes(',');
        const cleanNum = numPart.replace(/,/g, '');
        const decimals = cleanNum.includes('.') ? cleanNum.split('.')[1].length : 0;
        const target = parseFloat(cleanNum) || 0;

        return {
            prefix: prefix,
            target: target,
            suffix: suffix,
            decimals: decimals,
            hasCommas: hasCommas
        };
    },

    formatCounterValue(num, decimals = 0, hasCommas = false, prefix = '', suffix = '') {
        let formatted = decimals > 0 ? num.toFixed(decimals) : Math.round(num).toString();
        if (hasCommas) {
            const parts = formatted.split('.');
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            formatted = parts.join('.');
        }
        return `${prefix || ''}${formatted}${suffix || ''}`;
    },

    initStatsCounter() {
        const section = document.getElementById('stats-section') || document.querySelector('.stats-strip-section');
        const counters = document.querySelectorAll('.animated-counter');
        if (!counters.length) return;

        // Respect user's reduced-motion preference
        const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Parse each counter's configuration
        const items = Array.from(counters).map(el => {
            const rawTarget = el.getAttribute('data-target');
            const rawSuffix = el.getAttribute('data-suffix');
            const rawPrefix = el.getAttribute('data-prefix');
            const parsed = this.parseCounterValue(el.textContent, rawTarget, rawSuffix, rawPrefix);

            return {
                el: el,
                prefix: parsed.prefix,
                target: parsed.target,
                suffix: parsed.suffix,
                decimals: parsed.decimals,
                hasCommas: parsed.hasCommas,
                current: 0
            };
        });

        // If reduced motion is requested, render final target values immediately and exit without animation
        if (prefersReducedMotion) {
            items.forEach(item => {
                item.el.textContent = this.formatCounterValue(
                    item.target,
                    item.decimals,
                    item.hasCommas,
                    item.prefix,
                    item.suffix
                );
            });
            return;
        }

        // Initialize display to 0 formatted with prefixes/suffixes before scrolling into view
        items.forEach(item => {
            item.el.textContent = this.formatCounterValue(
                0,
                item.decimals,
                item.hasCommas,
                item.prefix,
                item.suffix
            );
        });

        let hasAnimated = false;
        let liveTimer = null;

        const triggerBump = (el) => {
            el.classList.remove('stat-bump');
            void el.offsetWidth;
            el.classList.add('stat-bump');
            setTimeout(() => el.classList.remove('stat-bump'), 550);
        };

        const startSlowLiveIncrements = (statItems) => {
            if (liveTimer) clearTimeout(liveTimer);

            const scheduleNext = () => {
                const delay = 4000 + Math.random() * 1000;
                liveTimer = setTimeout(() => {
                    // Cases Reported: +1 or +2
                    const reported = statItems.find(i => i.el.id === 'statCasesReported');
                    if (reported) {
                        const inc = Math.random() > 0.4 ? 1 : 2;
                        reported.current += inc;
                        reported.el.textContent = this.formatCounterValue(
                            reported.current,
                            reported.decimals,
                            reported.hasCommas,
                            reported.prefix,
                            reported.suffix
                        );
                        triggerBump(reported.el);
                    }

                    // Periodic realistic telemetry updates for Solved and In Progress
                    const coin = Math.random();
                    if (coin > 0.6) {
                        const solved = statItems.find(i => i.el.id === 'statCasesSolved');
                        if (solved) {
                            solved.current += 1;
                            solved.el.textContent = this.formatCounterValue(
                                solved.current,
                                solved.decimals,
                                solved.hasCommas,
                                solved.prefix,
                                solved.suffix
                            );
                            triggerBump(solved.el);
                        }
                    } else if (coin > 0.3) {
                        const progress = statItems.find(i => i.el.id === 'statInProgress');
                        if (progress) {
                            progress.current += 1;
                            progress.el.textContent = this.formatCounterValue(
                                progress.current,
                                progress.decimals,
                                progress.hasCommas,
                                progress.prefix,
                                progress.suffix
                            );
                            triggerBump(progress.el);
                        }
                    }

                    scheduleNext();
                }, delay);
            };

            scheduleNext();
        };

        const runCountUpAnimation = () => {
            if (hasAnimated) return;
            hasAnimated = true;

            const duration = 1750; // Smooth 1.75s animation
            const startTime = performance.now();

            counters.forEach(c => c.classList.add('counting-rapid'));

            // Smooth quartic ease-out curve
            const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4);

            const tick = (now) => {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = easeOutQuart(progress);

                items.forEach(item => {
                    const currentVal = eased * item.target;
                    item.current = currentVal;
                    item.el.textContent = this.formatCounterValue(
                        currentVal,
                        item.decimals,
                        item.hasCommas,
                        item.prefix,
                        item.suffix
                    );
                });

                if (progress < 1) {
                    requestAnimationFrame(tick);
                } else {
                    // Animation complete: lock in exact target values so they remain visible permanently
                    items.forEach(item => {
                        item.current = item.target;
                        item.el.textContent = this.formatCounterValue(
                            item.target,
                            item.decimals,
                            item.hasCommas,
                            item.prefix,
                            item.suffix
                        );
                        item.el.classList.remove('counting-rapid');
                    });

                    // Follow up with subtle live telemetry increments every 4-5 seconds
                    startSlowLiveIncrements(items);
                }
            };

            requestAnimationFrame(tick);
        };

        // Trigger animation strictly ONCE per page load when section enters viewport
        if ('IntersectionObserver' in window && section) {
            const observer = new IntersectionObserver((entries, obs) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !hasAnimated) {
                        // Immediately unobserve and disconnect so it never fires again
                        obs.unobserve(entry.target);
                        obs.disconnect();
                        runCountUpAnimation();
                    }
                });
            }, {
                threshold: 0.25,
                rootMargin: '0px 0px -30px 0px'
            });

            observer.observe(section);
        } else {
            // Fallback for environments without IntersectionObserver
            setTimeout(runCountUpAnimation, 400);
        }
    },

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.theme);
    },

    applyTheme(theme) {
        this.theme = theme;
        localStorage.setItem('cs_theme', theme);
        document.documentElement.setAttribute('data-theme', theme);

        // Update any theme icons
        document.querySelectorAll('.theme-toggle-btn i').forEach(icon => {
            if (theme === 'dark') {
                icon.className = 'fa-solid fa-sun';
            } else {
                icon.className = 'fa-solid fa-moon';
            }
        });
    },

    toggleLanguage() {
        this.lang = this.lang === 'en' ? 'hi' : 'en';
        this.applyLanguage(this.lang);
    },

    applyLanguage(lang) {
        if (!CyberShieldI18n[lang]) return;
        this.lang = lang;
        localStorage.setItem('cs_lang', lang);

        // Update badge text in navbar
        document.querySelectorAll('.lang-text-badge').forEach(badge => {
            badge.innerText = lang.toUpperCase();
        });

        // Translate data-i18n elements safely without removing icons or overwriting animated counters
        document.querySelectorAll('[data-i18n]').forEach(el => {
            if (el.classList.contains('animated-counter')) return;

            const key = el.getAttribute('data-i18n');
            const translation = CyberShieldI18n[lang][key];
            if (translation) {
                if (el.tagName === 'INPUT' && el.placeholder) {
                    el.placeholder = translation;
                } else {
                    const icon = el.querySelector('i');
                    if (icon) {
                        const iconHtml = icon.outerHTML;
                        el.innerHTML = `${iconHtml} <span>${translation}</span>`;
                    } else {
                        el.innerText = translation;
                    }
                }
            }
        });
    },

    copyText(text) {
        if (!text) return;
        navigator.clipboard.writeText(text).then(() => {
            this.showToast(`Copied to clipboard: ${text.substring(0, 16)}...`, 'success');
        }).catch(() => {
            this.showToast('Copied to clipboard', 'info');
        });
    },

    showToast(message, type = 'info') {
        this.setupToastContainer();
        const container = document.getElementById('csToastContainer');
        const toast = document.createElement('div');
        toast.className = `cs-toast cs-toast-${type}`;
        
        let icon = 'fa-circle-info';
        if (type === 'success') icon = 'fa-circle-check';
        if (type === 'danger' || type === 'error') icon = 'fa-triangle-exclamation';
        if (type === 'warning') icon = 'fa-circle-exclamation';

        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => {
                if (toast.parentElement) toast.remove();
            }, 300);
        }, 3000);
    }
};

// Expose globally
window.CyberShield = CyberShield;
window.toggleTheme = () => CyberShield.toggleTheme();
window.toggleLanguage = () => CyberShield.toggleLanguage();
window.copyText = (t) => CyberShield.copyText(t);

document.addEventListener('DOMContentLoaded', () => {
    CyberShield.init();
});
