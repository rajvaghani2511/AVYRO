import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_database_uri():
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

        # Strip unsupported query parameters for pg8000 driver safely
        if "pg8000" in db_url and "?" in db_url:
            base_part, query_part = db_url.split("?", 1)
            allowed_params = []
            for item in query_part.split("&"):
                is_invalid = False
                for prefix in ['sslmode=', 'ssl=', 'channel_binding=', 'gssencmode=']:
                    if item.startswith(prefix):
                        is_invalid = True
                        break
                if not is_invalid:
                    allowed_params.append(item)
            db_url = base_part + ("?" + "&".join(allowed_params) if allowed_params else "")

    if is_serverless and db_url and ('localhost' in db_url or '127.0.0.1' in db_url):
        db_url = None

    if db_url:
        return db_url
    elif is_serverless:
        tmp_db_path = '/tmp/avyro.db'
        bundled_db_path = os.path.join(BASE_DIR, 'instance', 'avyro.db')
        try:
            os.makedirs('/tmp', exist_ok=True)
            if not os.path.exists(tmp_db_path) and os.path.exists(bundled_db_path):
                shutil.copyfile(bundled_db_path, tmp_db_path)
        except Exception as e:
            print(f"Serverless DB Copy Notice: {e}")
            
        return 'sqlite:////tmp/avyro.db'
    else:
        return f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'avyro.db')}"


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'avyro-dev-secret-key-987654321'

    is_serverless = (
        os.environ.get('VERCEL') is not None or
        os.environ.get('VERCEL_ENV') is not None or
        os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None or
        os.environ.get('LAMBDA_TASK_ROOT') is not None or
        not os.access(BASE_DIR, os.W_OK)
    )

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if is_serverless:
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
