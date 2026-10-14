import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cybershield-secret-key-2026-secure-session-investigation')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'cybershield.db'))
    
    # Upload and Storage configurations
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads' / 'evidence'))
    REPORT_FOLDER = os.environ.get('REPORT_FOLDER', str(BASE_DIR / 'uploads' / 'reports'))
    SAMPLE_FOLDER = os.environ.get('SAMPLE_FOLDER', str(BASE_DIR / 'uploads' / 'sample_evidence'))
    
    # Upload limits: 25MB max per request
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'txt'}
    
    # Roles
    ROLE_CITIZEN = 'citizen'
    ROLE_INVESTIGATOR = 'investigator'
    ROLE_ADMIN = 'admin'
    
    # Standard Incident Categories
    CATEGORIES = [
        'Online Payment Fraud / UPI Scam',
        'Phishing & Credential Harvesting',
        'Identity Theft & Impersonation',
        'Social Media Fraud & Extortion',
        'Work-From-Home / Investment Scam',
        'E-Commerce & Online Marketplace Scam'
    ]
    
    # Standard Case Statuses
    STATUSES = [
        'Submitted',
        'Under Review',
        'Analysis In Progress',
        'Evidence Verified',
        'Report Generated',
        'Closed'
    ]
