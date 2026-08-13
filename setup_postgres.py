import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

DB_USER = "postgres"
DB_PASS = "raj2511"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "avyro_db"

def setup_postgres():
    print(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT} as user '{DB_USER}'...")
    try:
        # Connect to default postgres database to create avyro_db
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if avyro_db exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"PostgreSQL database '{DB_NAME}' created successfully!")
        else:
            print(f"PostgreSQL database '{DB_NAME}' already exists.")

        cursor.close()
        conn.close()

        # Generate connection URI
        pg_uri = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        # Write .env file
        env_content = f"""SECRET_KEY=avyro-super-secret-key-2026
DATABASE_URL={pg_uri}
FLASK_ENV=development
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("Updated .env file with PostgreSQL DATABASE_URL!")
        print(f"Connection URI: {pg_uri}")

    except Exception as e:
        print(f"PostgreSQL setup error: {e}")

if __name__ == '__main__':
    setup_postgres()
