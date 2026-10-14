import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test():
    print("Testing /api/cases ...")
    cases_resp = json.loads(urllib.request.urlopen('http://127.0.0.1:5000/api/cases').read())
    print('STATS:', cases_resp['stats'])
    print('CASES COUNT:', len(cases_resp['cases']))
    for c in cases_resp['cases']:
        print(f"  Case {c['id']}: {c['case_id']} | Status: {c['status']} | {c['title']} | Loss: INR {c['loss_amount']}")

    print("\nTesting /api/case/<id> details ...")
    for cid in [1, 2, 3]:
        det = json.loads(urllib.request.urlopen(f'http://127.0.0.1:5000/api/case/{cid}').read())
        print(f"  Case {cid} ({det['case']['case_id']}): Title='{det['case']['title']}' | Status='{det['case']['status']}'")
        print(f"    - Files ({len(det['evidence_files'])}): {[f['original_filename'] for f in det['evidence_files']]}")
        safe_entities = [e['entity_value'].replace('\u20b9', 'INR ') for e in det['entities']]
        print(f"    - Entities ({len(det['entities'])}): {safe_entities}")
        print(f"    - Findings ({len(det['findings'])}): {[f['title'] for f in det['findings']]}")
        print(f"    - Events ({len(det['timeline'])}): {[ev['title'] for ev in det['timeline']]}")

    print("\nTesting PDF Report Generation for Cases 1, 2, 3 ...")
    for cid in [1, 2, 3]:
        req = urllib.request.Request(f'http://127.0.0.1:5000/investigator/case/{cid}/report/download')
        resp = urllib.request.urlopen(req)
        content = resp.read()
        print(f"  Case {cid} PDF Report: HTTP {resp.status}, Content-Type: {resp.headers.get('Content-Type')}, Size: {len(content)} bytes")

    print("\nTesting Frontend Pages ...")
    for page in ['/pages/dashboard.html', '/pages/cases.html', '/pages/case-details.html?id=1', '/pages/case-details.html?id=2', '/pages/case-details.html?id=3']:
        resp = urllib.request.urlopen(f'http://127.0.0.1:5000{page}')
        print(f"  {page}: HTTP {resp.status}, Size: {len(resp.read())} bytes")

    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test()
