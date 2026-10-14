import urllib.request
import urllib.parse
import json
import os
import re
import sys
import http.cookiejar

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"

def audit():
    print("=================================================================")
    print("  CYBERSHIELD COMPREHENSIVE END-TO-END SYSTEM AUDIT")
    print("=================================================================")
    errors = []
    warnings = []

    # 1. CHECK ALL PAGES
    pages = [
        ("/", "Root Landing Page"),
        ("/index.html", "Landing Page (direct)"),
        ("/pages/login.html", "Login / Authentication"),
        ("/pages/dashboard.html", "Investigator Dashboard"),
        ("/pages/cases.html", "Cases Directory"),
        ("/pages/report-incident.html", "Citizen Complaint Intake"),
        ("/pages/case-details.html", "Case Workbench (default)"),
        ("/pages/case-details.html?id=1", "Case 1: Pending Verification"),
        ("/pages/case-details.html?id=2", "Case 2: Evidence Verified"),
        ("/pages/case-details.html?id=3", "Case 3: Already Completed"),
        ("/pages/evidence-vault.html", "Evidence Vault"),
        ("/pages/analysis-results.html", "OCR & Analysis Results"),
        ("/pages/incident-timeline.html", "Incident Timeline"),
        ("/pages/evidence-graph.html", "Evidence Graph"),
        ("/pages/profile.html", "Officer Profile"),
    ]

    print("\n[STEP 1] Testing HTTP availability of all pages...")
    for path, desc in pages:
        url = BASE_URL + path
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'CyberShieldAudit/1.0'})
            res = urllib.request.urlopen(req)
            status = res.status
            size = len(res.read())
            if status == 200:
                print(f"  [OK] 200 OK  {path:<32} ({desc}) [{size:,} bytes]")
            else:
                errors.append(f"{path} returned unexpected status {status}")
                print(f"  [FAIL] {status} {path}")
        except Exception as e:
            errors.append(f"{path} failed to load: {e}")
            print(f"  [FAIL] {path}: {e}")

    # 2. CHECK STATIC ASSETS (CSS & JS)
    assets = [
        "/css/style.css",
        "/css/components.css",
        "/css/dashboard.css",
        "/css/forms.css",
        "/css/evidence.css",
        "/css/analysis.css",
        "/css/responsive.css",
        "/js/main.js",
        "/js/navigation.js",
        "/js/dashboard.js",
        "/js/cases.js",
        "/js/report-incident.js",
        "/js/case-details.js",
        "/js/evidence.js",
        "/js/analysis.js",
        "/js/timeline.js",
        "/js/evidence-graph.js",
    ]

    print("\n[STEP 2] Testing all CSS & JavaScript bundles...")
    for path in assets:
        url = BASE_URL + path
        try:
            res = urllib.request.urlopen(url)
            size = len(res.read())
            print(f"  [OK] 200 OK  {path:<28} [{size:,} bytes]")
        except Exception as e:
            errors.append(f"Asset {path} failed: {e}")
            print(f"  [FAIL] {path}: {e}")

    # 3. CHECK BACKEND APIs
    print("\n[STEP 3] Testing Backend APIs & Data Integrity...")
    
    # /api/cases
    try:
        res = urllib.request.urlopen(BASE_URL + "/api/cases")
        data = json.loads(res.read())
        stats = data.get('stats', {})
        cases = data.get('cases', [])
        print(f"  [OK] /api/cases returned {len(cases)} cases.")
        print(f"       Stats: Total={stats.get('total_cases')}, Pending={stats.get('pending_cases')}, Verified={stats.get('verified_cases')}, Completed={stats.get('completed_cases')}")
        if len(cases) != 3:
            warnings.append(f"Expected exactly 3 cases, got {len(cases)}")
    except Exception as e:
        errors.append(f"/api/cases error: {e}")
        print(f"  [FAIL] /api/cases: {e}")

    # /api/case/<id> for 1, 2, 3
    for cid in [1, 2, 3]:
        try:
            res = urllib.request.urlopen(f"{BASE_URL}/api/case/{cid}")
            det = json.loads(res.read())
            c = det['case']
            evs = det['evidence_files']
            ents = det['entities']
            finds = det['findings']
            tl = det['timeline']
            print(f"  [OK] /api/case/{cid} -> {c['case_id']}: '{c['title'][:35]}...'")
            print(f"       Status: '{c['status']}', Loss: INR {c['loss_amount']:,}, Files: {len(evs)}, Entities: {len(ents)}, Findings: {len(finds)}, Events: {len(tl)}")
        except Exception as e:
            errors.append(f"/api/case/{cid} error: {e}")
            print(f"  [FAIL] /api/case/{cid}: {e}")

    # 4. CHECK AUTHENTICATION WORKFLOWS (COOKIE & SESSIONS)
    print("\n[STEP 4] Testing Citizen OTP & Demo Authentication...")
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # A. Citizen Demo Login
    try:
        req = urllib.request.Request(f"{BASE_URL}/auth/demo/citizen")
        res = opener.open(req)
        # Verify /api/auth/me recognizes logged-in citizen
        res_me = opener.open(f"{BASE_URL}/api/auth/me")
        me_data = json.loads(res_me.read())
        if me_data.get('authenticated') and me_data.get('user', {}).get('role') == 'citizen':
            print(f"  [OK] Citizen Demo Auth Verified! Logged in as: {me_data['user']['full_name']} ({me_data['user']['role']})")
        else:
            errors.append("Citizen demo auth failed to establish session")
            print(f"  [FAIL] Citizen auth state: {me_data}")
    except Exception as e:
        errors.append(f"Citizen auth error: {e}")
        print(f"  [FAIL] Citizen auth: {e}")

    # B. Investigator Demo Login
    cj2 = http.cookiejar.CookieJar()
    opener2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj2))
    try:
        req = urllib.request.Request(f"{BASE_URL}/auth/demo/investigator")
        res = opener2.open(req)
        # Verify /api/auth/me recognizes investigator
        res_me = opener2.open(f"{BASE_URL}/api/auth/me")
        me_data = json.loads(res_me.read())
        if me_data.get('authenticated') and me_data.get('user', {}).get('role') == 'investigator':
            print(f"  [OK] Investigator Demo Auth Verified! Logged in as: {me_data['user']['full_name']} (Badge: {me_data['user'].get('badge_number')})")
        else:
            errors.append("Investigator demo auth failed to establish session")
            print(f"  [FAIL] Investigator auth state: {me_data}")
    except Exception as e:
        errors.append(f"Investigator auth error: {e}")
        print(f"  [FAIL] Investigator auth: {e}")

    # 5. CHECK PDF REPORT DOWNLOADS FOR ALL 3 CASES
    print("\n[STEP 5] Testing ReportLab Dynamic PDF Generation...")
    for cid in [1, 2, 3]:
        try:
            req = urllib.request.Request(f"{BASE_URL}/investigator/case/{cid}/report/download")
            res = urllib.request.urlopen(req)
            data = res.read()
            mime = res.headers.get('Content-Type')
            is_pdf = data.startswith(b'%PDF')
            if is_pdf and res.status == 200:
                print(f"  [OK] Case {cid} PDF Report Generated: {len(data):,} bytes, MIME: {mime}")
            else:
                errors.append(f"Case {cid} PDF report download invalid format")
                print(f"  [FAIL] Case {cid} PDF is invalid")
        except Exception as e:
            errors.append(f"Case {cid} PDF download error: {e}")
            print(f"  [FAIL] Case {cid} PDF error: {e}")

    # 6. SCAN HTML FILES FOR INTEGRITY
    print("\n[STEP 6] Scanning HTML source files for script/stylesheet tags...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    html_files = []
    for root, _, files in os.walk(frontend_dir):
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))

    for hf in html_files:
        rel_name = os.path.relpath(hf, frontend_dir)
        with open(hf, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check script srcs
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content)
        for s in scripts:
            if s.startswith('/') and not s.startswith('//'):
                # Local static file
                local_path = os.path.join(frontend_dir, s.lstrip('/'))
                if not os.path.exists(local_path):
                    errors.append(f"Missing script in {rel_name}: {s}")
                    print(f"  [FAIL] {rel_name} links to missing script: {s}")

        # Check css hrefs
        styles = re.findall(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']stylesheet["\']', content)
        for st in styles:
            if st.startswith('/') and not st.startswith('//'):
                local_path = os.path.join(frontend_dir, st.lstrip('/'))
                if not os.path.exists(local_path):
                    errors.append(f"Missing stylesheet in {rel_name}: {st}")
                    print(f"  [FAIL] {rel_name} links to missing style: {st}")

    print("  [OK] All script and style tags verified across all HTML files.")

    # 7. SUMMARY
    print("\n=================================================================")
    print("  AUDIT SUMMARY")
    print("=================================================================")
    if not errors and not warnings:
        print("  🎉 PERFECT PASS! All 15 routes, 17 assets, 3 cases, auth sessions, and PDF reports are working with zero errors.")
    else:
        if errors:
            print(f"  ❌ Found {len(errors)} error(s):")
            for e in errors:
                print(f"     - {e}")
        if warnings:
            print(f"  ⚠️ Found {len(warnings)} warning(s):")
            for w in warnings:
                print(f"     - {w}")

if __name__ == '__main__':
    audit()
