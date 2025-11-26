"""
Quick script to investigate the users table structure
"""

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "khamarbari")
)

cursor = conn.cursor()

print("=== Users Table Info ===\n")

# Get table structure
cursor.execute("DESCRIBE users")
print("Columns:")
for col in cursor.fetchall():
    print(f"  {col}")

print("\n")

# Get primary keys
cursor.execute("""
    SELECT COLUMN_NAME, CONSTRAINT_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'users'
    AND CONSTRAINT_NAME = 'PRIMARY'
""")
print("Primary Keys:")
for col in cursor.fetchall():
    print(f"  {col}")

print("\n")

# Get all keys
cursor.execute("""
    SHOW KEYS FROM users
""")
print("All Keys:")
for key in cursor.fetchall():
    print(f"  {key}")

print("\n")

# Get sample data
cursor.execute("SELECT * FROM users LIMIT 1")
print("Sample Row (columns):")
print(f"  {cursor.column_names}")

cursor.close()
conn.close()
