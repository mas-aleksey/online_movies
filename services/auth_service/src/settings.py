import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve(strict=True).parent
DOCS_DIR = BASE_DIR.joinpath('docs')
TEMPLATE_DIR = BASE_DIR.joinpath('template')

SECRET_KEY = os.getenv('SECRET_KEY')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

ACCESS_EXPIRES = timedelta(minutes=30)
REFRESH_EXPIRES = timedelta(days=1)
FIRST_START = bool(int(os.getenv('FIRST_START', '0')))

DATABASE = {
    'drivername': 'postgresql+psycopg2',
    'host': os.getenv('DATABASE_HOST') or '127.0.0.1',
    'port': os.getenv('DATABASE_PORT') or 5432,
    'database': os.getenv('DATABASE_NAME') or 'auth',
    'username': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
}

REDIS_DNS = {
    'host': os.getenv('REDIS_HOST') or 'localhost',
    'port': os.getenv('REDIS_PORT') or 6379,
    'db': 0
}

OAUTH = {
    'Google': {
        'name': 'google',
        'server_metadata_url': 'https://accounts.google.com/.well-known/openid-configuration',
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'client_kwargs': {
            'scope': 'openid email profile'
        }
    }
}

RECAPTCHA_PUBLIC_KEY = '6Lerir4aAAAAAFbgWUf-DBrBYsG957HPj5kc_T_H'
DEFAULT_ROLE = 'free'
ROLES = [DEFAULT_ROLE, 'standard', 'extra']
SUPER_USER = {
    'email': os.getenv('SUPER_EMAIL'),
    'password': os.getenv('SUPER_PASS'),
}
