import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'avyro.db')

if not os.path.exists(DB_PATH):
    # Fallback to root avyro.db if exists
    DB_PATH = os.path.join(BASE_DIR, 'avyro.db')

def view_database():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}. Please run `python seed.py` first.")
        return

    print("==================================================")
    print(f"  AVYRO Database Inspector: {DB_PATH}")
    print("==================================================\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]

    print(f"Found {len(tables)} tables: {', '.join(tables)}\n")

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"--- Table: {table} ({count} rows) ---")

        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Columns: {', '.join(columns)}")

        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print("  ", row)
        print()

    conn.close()

if __name__ == '__main__':
    view_database()
