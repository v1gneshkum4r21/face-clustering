import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def get_env_bool(key, default='false'):
    return os.getenv(key, default).lower() == 'true'

def get_env_int(key, default):
    return int(os.getenv(key, default))

# Security Configuration
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD must be set in .env file")

JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET must be set in .env file")

SESSION_EXPIRY = get_env_int('SESSION_EXPIRY', '3600')

# Email Configuration
EMAIL_CONFIG = {
    'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'SMTP_PORT': get_env_int('SMTP_PORT', '587'),
    'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
    'FROM_EMAIL': os.getenv('FROM_EMAIL'),
    'USE_TLS': get_env_bool('USE_TLS', 'true')
}

# Validate email configuration
if not all([
    EMAIL_CONFIG['SMTP_USERNAME'],
    EMAIL_CONFIG['SMTP_PASSWORD'],
    EMAIL_CONFIG['FROM_EMAIL']
]):
    raise ValueError("""
    Email configuration incomplete. Please check:
    1. SMTP_USERNAME is set
    2. SMTP_PASSWORD is set (16-character App Password)
    3. FROM_EMAIL is set
    """)

# File Upload Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = get_env_int('MAX_CONTENT_LENGTH', '16777216')

# App Configuration
APP_NAME = os.getenv('APP_NAME', 'Face Recognition System')
ADMIN_CONTACT = os.getenv('ADMIN_CONTACT', 'admin@example.com')
DEBUG = get_env_bool('DEBUG')