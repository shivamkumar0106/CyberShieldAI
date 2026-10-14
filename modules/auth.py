from functools import wraps
import random
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from modules.audit import log_audit

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect('/pages/login.html')
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to continue.', 'warning')
                return redirect('/pages/login.html')
            user_role = session.get('role')
            if user_role not in allowed_roles:
                flash('Access denied: You do not have permission for this resource.', 'danger')
                if user_role == 'citizen':
                    return redirect('/pages/report-incident.html')
                return redirect('/pages/dashboard.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/me')
def auth_me():
    """Current session verification API."""
    if 'user_id' in session:
        db = get_db()
        user = db.execute(
            "SELECT id, username, email, full_name, role, phone, badge_number FROM users WHERE id = ?",
            (session['user_id'],)
        ).fetchone()
        if user:
            return jsonify({
                'authenticated': True,
                'user': dict(user)
            })
    return jsonify({
        'authenticated': False,
        'user': None
    })

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ? OR username = ?',
            (identifier, identifier)
        ).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['badge_number'] = user['badge_number']
            session['phone'] = user['phone']
            
            log_audit(db, 'USER_LOGIN', user_id=user['id'], details={'role': user['role']})
            flash(f'Welcome back, {user["full_name"]}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user['role'] in ('investigator', 'admin'):
                return redirect('/pages/dashboard.html')
            return redirect('/pages/report-incident.html')
        else:
            flash('Invalid email/username or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/citizen-otp', methods=['POST'])
def citizen_otp_login():
    """Mobile OTP verification login for citizens."""
    data = request.get_json(silent=True) or request.form
    phone = data.get('phone', '').strip().replace(' ', '').replace('-', '')
    otp = data.get('otp', '').strip()

    if not phone or len(phone) < 10:
        return jsonify({'status': 'error', 'message': 'Please provide a valid 10-digit mobile number.'}), 400

    if not otp:
        return jsonify({'status': 'error', 'message': 'Please enter the verification OTP.'}), 400

    db = get_db()
    
    # Check for existing citizen with this phone number
    user = db.execute(
        "SELECT * FROM users WHERE (phone LIKE ? OR phone = ?) AND role = 'citizen'",
        (f"%{phone[-10:]}%", phone)
    ).fetchone()

    if not user:
        # Create a new citizen user record
        clean_phone = f"+91 {phone[-10:]}"
        username = f"citizen_{phone[-4:]}_{random.randint(100, 999)}"
        email = f"{username}@citizen.cybershield.local"
        default_name = f"Citizen User ({phone[-4:]})"
        pwd_hash = generate_password_hash("citizen_otp_auth")

        cursor = db.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role, phone)
            VALUES (?, ?, ?, ?, 'citizen', ?)
        """, (username, email, pwd_hash, default_name, clean_phone))
        db.commit()
        user_id = cursor.lastrowid
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    # Establish citizen session
    session.permanent = True
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['full_name'] = user['full_name']
    session['role'] = 'citizen'
    session['phone'] = user['phone']
    session['badge_number'] = None

    log_audit(db, 'CITIZEN_OTP_LOGIN', user_id=user['id'], details={'phone': user['phone']})

    if request.is_json:
        return jsonify({
            'status': 'success',
            'message': f"Verified as {user['full_name']}",
            'redirect_url': '/pages/report-incident.html',
            'user': {
                'id': user['id'],
                'full_name': user['full_name'],
                'role': 'citizen',
                'phone': user['phone']
            }
        })
    
    return redirect('/pages/report-incident.html')

@auth_bp.route('/demo-login/<role>')
@auth_bp.route('/demo/<role>')
def demo_login(role):
    """Quick demo switcher for testing the platform with pre-configured roles."""
    role_map = {
        'investigator': ('investigator@cybershield.local', 'Inspector Sharma'),
        'citizen': ('citizen@cybershield.local', 'Aarav Patel (Victim)'),
        'admin': ('admin@cybershield.local', 'Chief Admin officer')
    }
    if role not in role_map:
        flash('Invalid demo role.', 'danger')
        return redirect('/pages/login.html')
        
    db = get_db()
    email = role_map[role][0]
    user = db.execute('SELECT * FROM users WHERE email = ? OR role = ? ORDER BY id ASC LIMIT 1', (email, role)).fetchone()
    if not user:
        flash('Demo accounts not yet initialized.', 'warning')
        return redirect('/pages/login.html')

    session.permanent = True
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['full_name'] = user['full_name']
    session['role'] = user['role']
    session['badge_number'] = user['badge_number']
    session['phone'] = user['phone']

    log_audit(db, 'DEMO_LOGIN', user_id=user['id'], details={'role': user['role']})
    flash(f'Logged in as demo user: {user["full_name"]} ({user["role"].upper()})', 'info')

    # ROLE-SPECIFIC DESTINATIONS:
    if user['role'] in ('investigator', 'admin'):
        return redirect('/pages/dashboard.html')
    # Citizen goes directly to the incident intake report form!
    return redirect('/pages/report-incident.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        try:
            db = get_db()
            log_audit(db, 'USER_LOGOUT', user_id=user_id)
        except Exception:
            pass
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect('/pages/login.html')
