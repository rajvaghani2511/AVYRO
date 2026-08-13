import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'avyro-dev-secret-key-987654321'

    # Detect Vercel / AWS Lambda / Read-Only Serverless Container Environment
    is_serverless = (
        os.environ.get('VERCEL') is not None or
        os.environ.get('VERCEL_ENV') is not None or
        os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None or
        os.environ.get('LAMBDA_TASK_ROOT') is not None or
        not os.access(BASE_DIR, os.W_OK)
    )

    db_url = os.environ.get('DATABASE_URL')

    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        if db_url.startswith("postgresql://") and "postgresql+pg8000://" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)

        if "pg8000" in db_url:
            db_url = db_url.replace("?sslmode=require", "").replace("&sslmode=require", "")

    if is_serverless and db_url and ('localhost' in db_url or '127.0.0.1' in db_url):
        db_url = None

    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    elif is_serverless:
        # Pre-populate /tmp/avyro.db from bundled instance/avyro.db if available
        tmp_db_path = '/tmp/avyro.db'
        bundled_db_path = os.path.join(BASE_DIR, 'instance', 'avyro.db')
        try:
            os.makedirs('/tmp', exist_ok=True)
            if not os.path.exists(tmp_db_path) and os.path.exists(bundled_db_path):
                shutil.copyfile(bundled_db_path, tmp_db_path)
        except Exception as e:
            print(f"Serverless DB Copy Notice: {e}")
            
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/avyro.db'
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'avyro.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if is_serverless:
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
