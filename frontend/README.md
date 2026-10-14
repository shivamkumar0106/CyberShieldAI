# CyberShield — Frontend Architecture

CyberShield is a web-based cybercrime reporting and digital evidence investigation-support platform.

## Directory Structure

```text
CyberShield/
└── frontend/
    ├── index.html
    ├── pages/
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── cases.html
    │   ├── report-incident.html
    │   ├── case-details.html
    │   ├── evidence-vault.html
    │   ├── analysis-results.html
    │   ├── incident-timeline.html
    │   ├── evidence-graph.html
    │   └── profile.html
    ├── css/
    │   ├── style.css
    │   ├── components.css
    │   ├── dashboard.css
    │   ├── forms.css
    │   ├── evidence.css
    │   ├── analysis.css
    │   └── responsive.css
    ├── js/
    │   ├── main.js
    │   ├── navigation.js
    │   ├── dashboard.js
    │   ├── cases.js
    │   ├── report-incident.js
    │   ├── evidence.js
    │   ├── analysis.js
    │   ├── timeline.js
    │   └── evidence-graph.js
    ├── assets/
    │   ├── images/
    │   ├── icons/
    │   └── fonts/
    └── README.md
```

## Typography Specifications
- **Headings**: `Manrope` (weights: 600, 700, 800)
- **Body, Buttons, & Form Elements**: `DM Sans` (weights: 400, 500, 600)
- **Complaint IDs & Technical Details**: `JetBrains Mono` (weights: 500, 600)

## Theming & Multilingual Engine
- **Dark and Light Theme**: Toggleable with the sun/moon icon on every page. Automatically remembers user choice in `localStorage ('cs_theme')`.
- **Multilingual (English & Hindi)**: Instant bilingual switching using `CyberShield.toggleLanguage()`. Automatically remembers user preference in `localStorage ('cs_lang')`.

## Authentication & Demo Profiles
The login screen features clean ID and password inputs along with instant 1-click demo access:
- **Citizen Demo**: `citizen@cybershield.local` (Aarav Patel)
- **Investigator Demo**: `investigator@cybershield.local` (Inspector Sharma)
