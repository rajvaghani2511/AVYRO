import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'avyro-dev-secret-key-987654321'

    # Database URI configuration for local vs Vercel / Remote DB
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    elif os.environ.get('VERCEL'):
        # Vercel serverless environment uses /tmp for writeable SQLite fallback
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/avyro.db'
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'avyro.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
