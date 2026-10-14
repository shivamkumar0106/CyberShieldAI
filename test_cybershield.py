import unittest
import os
import json
from app import create_app
from database import get_standalone_db
from config import Config
from modules.evidence import calculate_sha256, verify_file_integrity
from modules.extraction import extract_entities_from_text
from modules.verification import run_cross_evidence_verification
from modules.timeline import reconstruct_case_timeline
from modules.relationship_graph import generate_cytoscape_graph
from modules.reports import generate_pdf_report

class CyberShieldSystemTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.db = get_standalone_db()

    def tearDown(self):
        self.db.close()

    def test_01_database_tables(self):
        """Verify all 12 core tables exist."""
        cursor = self.db.cursor()
        tables = [
            'users', 'cases', 'evidence_files', 'analysis_runs',
            'extracted_text', 'entities', 'events', 'findings',
            'entity_evidence_links', 'investigator_notes', 'audit_logs', 'reports'
        ]
        for tbl in tables:
            res = cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbl}'").fetchone()
            self.assertIsNotNone(res, f"Table {tbl} must exist")

    def test_02_entity_extraction(self):
        """Test regex and NER for UPI, Phone, UTR, Amount, Email, URL."""
        sample_text = """
        User was asked to transfer Rs. 25,000 to UPI ID merchant.store@okaxis.
        Suspect contact number is +91 9823145670.
        Bank debit notification reference: UTR 928172645102.
        Phishing email received from scam.team@secure-portal.com.
        Deceptive website hosted at https://fake-sbi-portal.xyz/login.
        """
        entities = extract_entities_from_text(sample_text)
        types_found = {e['type'] for e in entities}
        self.assertIn('UPI_ID', types_found)
        self.assertIn('PHONE', types_found)
        self.assertIn('TXN_REF', types_found)
        self.assertIn('AMOUNT', types_found)
        self.assertIn('EMAIL', types_found)
        self.assertIn('URL_DOMAIN', types_found)

        # Check values
        upi = next(e for e in entities if e['type'] == 'UPI_ID')
        self.assertEqual(upi['normalized'], 'merchant.store@okaxis')

    def test_03_sha256_integrity(self):
        """Test SHA-256 calculation and tamper verification."""
        test_bytes = b"Digital Forensic Evidence Sample Content 2026"
        expected_hash = calculate_sha256(test_bytes)
        self.assertEqual(len(expected_hash), 64)

        # Check existing evidence in DB
        ef = self.db.execute("SELECT id FROM evidence_files LIMIT 1").fetchone()
        if ef:
            res = verify_file_integrity(ef['id'], self.db)
            self.assertTrue(res['matched'], "Pre-seeded file hash should match disk bytes")

    def test_04_cross_evidence_rules(self):
        """Test rule engine execution."""
        findings = run_cross_evidence_verification(1, self.db)
        self.assertGreater(len(findings), 0)
        categories = [f['category'] for f in findings]
        self.assertTrue('INTEGRITY_CHECK' in categories or 'MATCH_CONFIRMED' in categories)

    def test_05_timeline_reconstruction(self):
        """Test chronological timeline synthesis."""
        events = reconstruct_case_timeline(1, self.db)
        self.assertGreater(len(events), 0)
        # Ensure dates are non-empty
        for ev in events:
            self.assertTrue(bool(ev['event_date']))

    def test_06_cytoscape_graph_generation(self):
        """Test Cytoscape graph structure."""
        graph = generate_cytoscape_graph(1, self.db)
        nodes = graph['elements']['nodes']
        edges = graph['elements']['edges']
        self.assertGreater(len(nodes), 0)
        self.assertGreater(len(edges), 0)
        
        # Verify node properties
        sample_node = nodes[0]['data']
        self.assertIn('id', sample_node)
        self.assertIn('label', sample_node)
        self.assertIn('color', sample_node)

    def test_07_pdf_report_generation(self):
        """Test ReportLab PDF dossier export."""
        pdf_path, err = generate_pdf_report(1, 1, self.db)
        self.assertIsNone(err)
        self.assertIsNotNone(pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 1000)

    def test_08_routes_and_access(self):
        """Test key HTTP endpoints."""
        # 1. Landing page
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'CyberShield', resp.data)

        # 2. Login page
        resp = self.client.get('/auth/login')
        self.assertEqual(resp.status_code, 200)

        # 3. Track case page
        resp = self.client.get('/track?case_ref=CS-2026-10492')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'CS-2026-10492', resp.data)

        # 4. Demo Login as Investigator
        resp = self.client.get('/auth/demo-login/investigator', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Investigation Command Center', resp.data)

        # 5. Case detail workbench
        resp = self.client.get('/investigator/case/1')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Evidence Inventory', resp.data)

        # 6. Graph API endpoint
        resp = self.client.get('/api/case/1/graph')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn('elements', data)

        # 7. Audit logs page
        resp = self.client.get('/investigator/audit-logs')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Audit Trail', resp.data)

if __name__ == '__main__':
    unittest.main()
