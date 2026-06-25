import sqlite3
import os

print("🔥 Creating database...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "thyroid.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age REAL,
    gender TEXT,
    tsh REAL,
    t3 REAL,
    tt4 REAL,
    prediction TEXT,
    confidence REAL,
    source TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database ready at:", db_path)