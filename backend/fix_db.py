from config.db import get_connection
from dotenv import load_dotenv

load_dotenv()

def fix_database():
    print("Starting database fix...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        print("Checking if table 'cattles' exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cattles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                weight FLOAT
            )
        """)
        print(" -> Table 'cattles' checked/created.")

        print("Checking if table 'users' exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                owner_name VARCHAR(255) NOT NULL,
                farm_name VARCHAR(255) NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        print(" -> Table 'users' checked/created.")

        print("Checking if table 'medical_history' exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cattle_id INT NOT NULL,
                date DATE,
                name VARCHAR(255),
                diagnosis TEXT,
                FOREIGN KEY (cattle_id) REFERENCES cattles(id) ON DELETE CASCADE
            )
        """)
        print(" -> Table 'medical_history' checked/created.")
        
        # List of columns to ensure exist
        columns_to_add = [
            ("tag_number", "VARCHAR(50) UNIQUE"),
            ("breed", "VARCHAR(50)"),
            ("purpose", "VARCHAR(50)"),
            ("gender", "VARCHAR(20)"),
            ("dob", "DATE"),
            ("entry_date", "DATE"),
            ("initial_weight", "FLOAT"),
            ("current_weight", "FLOAT"),
            ("health_notes", "TEXT"),
            ("seller_name", "VARCHAR(100)"),
            ("seller_address", "VARCHAR(255)"),
            ("seller_phone", "VARCHAR(20)"),
            ("photo_path", "VARCHAR(255)"),
            ("documents_path", "VARCHAR(255)")
        ]

        for col_name, col_type in columns_to_add:
            try:
                print(f"Checking/Adding column: {col_name}")
                cursor.execute(f"ALTER TABLE cattles ADD COLUMN {col_name} {col_type}")
                print(f" -> Added {col_name}")
            except Exception as e:
                print(f" -> Skipped {col_name} (Reason: {e})")

        conn.commit()
        cursor.close()
        conn.close()
        print("Database fix completed.")
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    fix_database()
