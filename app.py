import os
from datetime import timedelta
from flask import Flask, render_template, session, g, jsonify, request, send_from_directory, redirect
from config import Config
from database import get_db, close_db, init_db
from modules.auth import auth_bp
from modules.cases import cases_bp

def create_app(config_class=Config):
    # Serve static assets and frontend structure directly from frontend/
    frontend_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
    app.config.from_object(config_class)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    # Teardown database connection
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(cases_bp)

    # Context Processor for standard session data in templates
    @app.context_processor
    def inject_user_context():
        user = None
        if 'user_id' in session:
            db = get_db()
            user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        return {
            'current_user': user,
            'is_authenticated': 'user_id' in session,
            'user_role': session.get('role'),
            'app_name': 'CyberShield'
        }

    # Custom Jinja Template Filters
    @app.template_filter('inr')
    def inr_format(val):
        try:
            return f"₹{float(val):,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    @app.template_filter('datetime_fmt')
    def datetime_filter(val):
        if not val:
            return "—"
        try:
            s = str(val)
            if len(s) >= 19:
                return s[:19].replace('T', ' ')
            return s
        except Exception:
            return str(val)

    # Root landing page
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    # Convenience shortcuts to modular pages
    @app.route('/login')
    def page_login():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'login.html')

    @app.route('/dashboard')
    def page_dashboard():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'dashboard.html')

    @app.route('/cases')
    def page_cases():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'cases.html')

    @app.route('/case-details')
    def page_case_details():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'case-details.html')

    @app.route('/report-incident')
    def page_report():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'report-incident.html')

    @app.route('/evidence-vault')
    def page_evidence_vault():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'evidence-vault.html')

    @app.route('/analysis-results')
    def page_analysis_results():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'analysis-results.html')

    @app.route('/incident-timeline')
    def page_timeline():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'incident-timeline.html')

    @app.route('/evidence-graph')
    def page_graph():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'evidence-graph.html')

    @app.route('/profile')
    def page_profile():
        return send_from_directory(os.path.join(app.static_folder, 'pages'), 'profile.html')

    # Dynamic API for Cases & Dashboard Stats
    @app.route('/api/cases')
    def api_get_cases():
        db = get_db()
        cases = db.execute("""
            SELECT c.*, u.full_name as complainant_name,
                   (SELECT COUNT(*) FROM evidence_files WHERE case_id = c.id) as evidence_count,
                   (SELECT COUNT(*) FROM findings WHERE case_id = c.id AND severity = 'HIGH') as high_flags
            FROM cases c
            LEFT JOIN users u ON c.user_id = u.id
            ORDER BY c.id ASC
        """).fetchall()

        total_cases = db.execute("SELECT COUNT(*) as cnt FROM cases").fetchone()['cnt']
        pending_cases = db.execute("SELECT COUNT(*) as cnt FROM cases WHERE status IN ('Submitted', 'Under Review')").fetchone()['cnt']
        verified_cases = db.execute("SELECT COUNT(*) as cnt FROM cases WHERE status IN ('Evidence Verified')").fetchone()['cnt']
        completed_cases = db.execute("SELECT COUNT(*) as cnt FROM cases WHERE status IN ('Completed', 'Report Generated')").fetchone()['cnt']
        total_evidence = db.execute("SELECT COUNT(*) as cnt FROM evidence_files").fetchone()['cnt']
        high_findings = db.execute("SELECT COUNT(*) as cnt FROM findings WHERE severity = 'HIGH'").fetchone()['cnt']

        return jsonify({
            'status': 'success',
            'stats': {
                'total_cases': total_cases,
                'pending_cases': pending_cases,
                'verified_cases': verified_cases,
                'completed_cases': completed_cases,
                'total_evidence': total_evidence,
                'high_findings': high_findings
            },
            'cases': [dict(c) for c in cases]
        })

    # Individual Case Detail API (For Dynamic Workbench)
    @app.route('/api/case/<int:case_id>')
    def api_get_case_detail(case_id):
        db = get_db()
        case = db.execute("""
            SELECT c.*, u.full_name as complainant_name, u.phone as complainant_phone, u.email as complainant_email
            FROM cases c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        """, (case_id,)).fetchone()

        if not case:
            return jsonify({'status': 'error', 'message': 'Case not found'}), 404

        evidence_files = db.execute("""
            SELECT ef.*,
                   (SELECT quality_score FROM extracted_text WHERE evidence_id = ef.id LIMIT 1) as quality_score,
                   (SELECT extraction_method FROM extracted_text WHERE evidence_id = ef.id LIMIT 1) as extraction_method,
                   (SELECT text_content FROM extracted_text WHERE evidence_id = ef.id LIMIT 1) as extracted_raw_text
            FROM evidence_files ef
            WHERE ef.case_id = ?
            ORDER BY ef.upload_time ASC
        """, (case_id,)).fetchall()

        entities = db.execute("""
            SELECT e.*, ef.original_filename
            FROM entities e
            JOIN evidence_files ef ON e.evidence_id = ef.id
            WHERE e.case_id = ?
            ORDER BY e.entity_type, e.id
        """, (case_id,)).fetchall()

        findings = db.execute("""
            SELECT * FROM findings
            WHERE case_id = ?
            ORDER BY CASE severity WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END
        """, (case_id,)).fetchall()

        events = db.execute("""
            SELECT * FROM events
            WHERE case_id = ?
            ORDER BY event_date ASC, event_time ASC
        """, (case_id,)).fetchall()

        return jsonify({
            'status': 'success',
            'case': dict(case),
            'evidence_files': [dict(e) for e in evidence_files],
            'entities': [dict(en) for en in entities],
            'findings': [dict(f) for f in findings],
            'timeline': [dict(ev) for ev in events]
        })

    # Global Session Verification API
    @app.route('/api/auth/me')
    def api_auth_me():
        if 'user_id' in session:
            db = get_db()
            user = db.execute(
                "SELECT id, username, email, full_name, role, phone, badge_number FROM users WHERE id = ?",
                (session['user_id'],)
            ).fetchone()
            if user:
                return jsonify({'authenticated': True, 'user': dict(user)})
        return jsonify({'authenticated': False, 'user': None})

    # Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    # Ensure database is prepared
    init_db()
    app = create_app()
    print("Starting CyberShield Application on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
