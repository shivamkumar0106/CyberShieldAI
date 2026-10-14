// CyberShield AI — Bilingual Translation Engine (English & Hindi)

const translations = {
    en: {
        // Navigation
        "nav_home": "Home",
        "nav_features": "Features",
        "nav_how_it_works": "How It Works",
        "nav_report": "Report Incident",
        "nav_track": "Track Case",
        "nav_workbench": "Investigator Workbench",
        "nav_audit": "Audit Trail",
        "nav_login": "Login",
        "nav_register": "Register",
        "nav_logout": "Sign Out",
        "nav_my_cases": "My Cases",
        "nav_quick_demo": "Quick Demo Access",
        "brand_subtitle": "Report · Analyze · Support",

        // Hero Section
        "hero_pill": "CYBERCRIME INVESTIGATION SUPPORT PLATFORM",
        "hero_title_1": "Turning Digital Evidence into",
        "hero_title_2": "Real Justice",
        "hero_desc": "CyberShield helps citizens report cybercrimes and assists investigators in collecting, analyzing and visualizing digital evidence from images, documents and metadata — faster, smarter and more securely.",
        "hero_btn_report": "Report an Incident",
        "hero_btn_demo": "Watch Demo",
        "hero_btn_workbench": "Open Workbench",
        "val_secure": "Secure",
        "val_efficient": "Efficient",
        "val_friendly": "Citizen Friendly",
        "val_support": "Investigation Support",

        // Features
        "feat_1_title": "Report & Upload Evidence",
        "feat_1_desc": "Submit cybercrime complaints with images, documents and transaction details.",
        "feat_2_title": "Automatic Evidence Analysis",
        "feat_2_desc": "Extract text, metadata and key information using OCR and entity recognition.",
        "feat_3_title": "Visualize Connections",
        "feat_3_desc": "Interactive timelines and relationship graphs to uncover critical link networks.",
        "feat_4_title": "Support Investigations",
        "feat_4_desc": "Organized evidence, consistency checks and downloadable PDF dossiers for investigators.",

        // Stats
        "stat_cases": "Cases Reported",
        "stat_files": "Evidence Files Processed",
        "stat_inv": "Investigators (Demo)",
        "stat_acc": "Processing Accuracy",

        // How it works
        "how_title": "How CyberShield Works",
        "step_1_title": "Report Incident",
        "step_1_desc": "Provide details and upload your available digital evidence.",
        "step_2_title": "Analyze Evidence",
        "step_2_desc": "Extract text, metadata and key entities automatically.",
        "step_3_title": "View Insights",
        "step_3_desc": "Timelines, relationship graphs and consistency checks.",
        "step_4_title": "Generate Report",
        "step_4_desc": "Download a structured investigation summary dossier.",

        // Quick Notice Banner
        "notice_title": "Investigation Support Scope:",
        "notice_desc": "CyberShield assists human investigators. It does not replace police FIRs, official police reporting portals, or statutory digital forensics labs.",

        // Common Actions
        "action_verify_hash": "Verify Hash",
        "action_download_pdf": "Download PDF Report",
        "action_rerun_analysis": "Re-Run Analysis",
        "action_track_case": "Track Case",
        "action_submit": "Submit Complaint",
        "action_filter": "Filter Cases",

        // Statuses
        "status_submitted": "Submitted",
        "status_under_review": "Under Review",
        "status_verified": "Evidence Verified",
        "status_report_gen": "Report Generated",
        "status_closed": "Closed"
    },
    hi: {
        // Navigation
        "nav_home": "होम",
        "nav_features": "विशेषताएं",
        "nav_how_it_works": "प्रक्रिया",
        "nav_report": "शिकायत दर्ज करें",
        "nav_track": "केस ट्रैक करें",
        "nav_workbench": "जांच कार्यक्षेत्र",
        "nav_audit": "ऑडिट लॉग",
        "nav_login": "लॉग इन",
        "nav_register": "पंजीकरण",
        "nav_logout": "साइन आउट",
        "nav_my_cases": "मेरी शिकायतें",
        "nav_quick_demo": "डेमो एक्सेस",
        "brand_subtitle": "रिपोर्ट · विश्लेषण · सहायता",

        // Hero Section
        "hero_pill": "साइबर अपराध डिजिटल जांच सहायता मंच",
        "hero_title_1": "डिजिटल साक्ष्यों को",
        "hero_title_2": "सच्चे न्याय में बदलना",
        "hero_desc": "साइबरशील्ड नागरिकों को साइबर अपराधों की रिपोर्ट करने और जांचकर्ताओं को स्क्रीनशॉट, पीडीएफ और मेटाडेटा से डिजिटल साक्ष्य निकालने, जांचने और विज़ुअलाइज़ करने में मदद करता है — सुरक्षित, तेज़ और पारदर्शी।",
        "hero_btn_report": "घटना की रिपोर्ट करें",
        "hero_btn_demo": "डेमो देखें",
        "hero_btn_workbench": "कार्यक्षेत्र खोलें",
        "val_secure": "सुरक्षित",
        "val_efficient": "कुशल",
        "val_friendly": "नागरिक अनुकूल",
        "val_support": "जांच सहायता",

        // Features
        "feat_1_title": "साक्ष्य अपलोड व रिपोर्टिंग",
        "feat_1_desc": "छवियों, दस्तावेजों और लेनदेन विवरण के साथ साइबर अपराध की शिकायतें दर्ज करें।",
        "feat_2_title": "स्वचालित साक्ष्य विश्लेषण",
        "feat_2_desc": "OCR और भाषा विश्लेषण द्वारा टेक्स्ट, मेटाडेटा और महत्वपूर्ण पहचानकर्ताओं को निकालें।",
        "feat_3_title": "संबंधों का दृश्य चित्रण",
        "feat_3_desc": "महत्वपूर्ण लिंक उजागर करने के लिए संवादात्मक घटनाक्रम और संबंध आरेख।",
        "feat_4_title": "जांच में सीधा सहयोग",
        "feat_4_desc": "जांचकर्ताओं के लिए सुव्यवस्थित साक्ष्य, विसंगति परीक्षण और डाउनलोड करने योग्य रिपोर्ट।",

        // Stats
        "stat_cases": "दर्ज मामले",
        "stat_files": "संसाधित साक्ष्य फाइलें",
        "stat_inv": "जांचकर्ता (डेमो)",
        "stat_acc": "सटीकता दर",

        // How it works
        "how_title": "साइबरशील्ड कैसे कार्य करता है",
        "step_1_title": "1. घटना दर्ज करें",
        "step_1_desc": "विवरण प्रदान करें और उपलब्ध डिजिटल साक्ष्य अपलोड करें।",
        "step_2_title": "2. साक्ष्य विश्लेषण",
        "step_2_desc": "टेक्स्ट, मेटाडेटा और यूपीआई/फोन विवरण स्वतः निकालें।",
        "step_3_title": "3. अंतर्दृष्टि देखें",
        "step_3_desc": "कालक्रम, संबंध आरेख और साक्ष्य सत्यापन जांचें।",
        "step_4_title": "4. रिपोर्ट तैयार करें",
        "step_4_desc": "संरचित जांच सारांश पीडीएफ डाउनलोड करें।",

        // Quick Notice Banner
        "notice_title": "जांच सहायता दायरा:",
        "notice_desc": "साइबरशील्ड मानव जांचकर्ताओं की सहायता करता है। यह आधिकारिक पुलिस प्राथमिकी (FIR) या फोरेंसिक प्रयोगशाला का स्थान नहीं लेता है।",

        // Common Actions
        "action_verify_hash": "हैश सत्यापित करें",
        "action_download_pdf": "पीडीएफ रिपोर्ट डाउनलोड करें",
        "action_rerun_analysis": "पुनः विश्लेषण करें",
        "action_track_case": "केस ट्रैक करें",
        "action_submit": "शिकायत जमा करें",
        "action_filter": "फिल्टर करें",

        // Statuses
        "status_submitted": "प्रस्तुत",
        "status_under_review": "समीक्षाधीन",
        "status_verified": "साक्ष्य सत्यापित",
        "status_report_gen": "रिपोर्ट तैयार",
        "status_closed": "समाप्त"
    }
};

let currentLanguage = localStorage.getItem('cybershield_lang') || 'en';

function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLanguage = lang;
    localStorage.setItem('cybershield_lang', lang);

    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            if (el.tagName === 'INPUT' && (el.type === 'button' || el.type === 'submit')) {
                el.value = translations[lang][key];
            } else if (el.tagName === 'INPUT' && el.placeholder) {
                el.placeholder = translations[lang][key];
            } else {
                el.innerHTML = translations[lang][key];
            }
        }
    });

    // Update Language Button Indicator
    const langBtnText = document.getElementById('currentLangLabel');
    if (langBtnText) {
        langBtnText.innerText = lang === 'hi' ? 'हिन्दी' : 'English';
    }
}

function toggleLanguage() {
    const nextLang = currentLanguage === 'en' ? 'hi' : 'en';
    setLanguage(nextLang);
}

document.addEventListener('DOMContentLoaded', function() {
    setLanguage(currentLanguage);
});
