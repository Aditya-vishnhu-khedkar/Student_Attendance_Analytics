import sqlite3

conn = sqlite3.connect("attendance.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    present INTEGER NOT NULL,
    total INTEGER NOT NULL
)
""")

conn.commit()
conn.close()

print("Database created successfully!")