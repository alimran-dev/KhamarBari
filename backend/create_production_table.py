"""
Database migration script to add production_entries table
Run this script to create the production_entries table in your database
"""

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def create_production_table():
    """Creates the production_entries table"""
    # Get database credentials from environment
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS production_entries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cattle_id INT NOT NULL,
        animal_tag VARCHAR(50) NOT NULL,
        animal_name VARCHAR(100),
        product_type ENUM('Milk', 'Eggs', 'Wool bale', 'Waste bin') NOT NULL,
        quantity DECIMAL(10, 2) NOT NULL,
        unit VARCHAR(20) NOT NULL,
        entry_time VARCHAR(20) NOT NULL,
        entry_date VARCHAR(20) NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (cattle_id) REFERENCES cattles(id) ON DELETE CASCADE,
        INDEX idx_animal_tag (animal_tag),
        INDEX idx_entry_date (entry_date),
        INDEX idx_product_type (product_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(create_table_query)
        conn.commit()
        print("✓ Production entries table created successfully!")
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'production_entries'")
        result = cursor.fetchone()
        if result:
            print("✓ Table verification: production_entries exists")
            
            # Show table structure
            cursor.execute("DESCRIBE production_entries")
            columns = cursor.fetchall()
            print("\nTable structure:")
            for column in columns:
                print(f"  - {column[0]}: {column[1]}")
        
    except Exception as e:
        print(f"✗ Error creating table: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Creating production_entries table...")
    create_production_table()
    print("\nMigration completed!")
