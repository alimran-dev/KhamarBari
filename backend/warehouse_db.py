"""
Database schema for warehouse management system
Creates tables for stock items, stock movements, and tracking
"""

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def create_warehouse_tables():
    """Creates all warehouse-related tables"""
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )
    cursor = conn.cursor()
    
    print("Creating warehouse tables...\n")
    
    # 1. Stock Items Table
    stock_items_table = """
    CREATE TABLE IF NOT EXISTS stock_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        item_name VARCHAR(200) NOT NULL,
        category ENUM('Feed', 'Medicine', 'Equipment', 'Products') NOT NULL,
        batch_no VARCHAR(100) NOT NULL,
        quantity DECIMAL(10, 2) NOT NULL DEFAULT 0,
        unit VARCHAR(50) NOT NULL,
        expiry_date DATE NULL,
        photo_path VARCHAR(500) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_category (category),
        INDEX idx_batch_no (batch_no),
        INDEX idx_expiry_date (expiry_date),
        INDEX idx_item_name (item_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(stock_items_table)
        conn.commit()
        print("✓ stock_items table created successfully")
    except Exception as e:
        print(f"✗ Error creating stock_items table: {str(e)}")
        conn.rollback()
    
    # 2. Stock Movements Table (for tracking all stock changes)
    stock_movements_table = """
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        stock_item_id INT NOT NULL,
        movement_type ENUM('Add', 'Remove', 'Transfer', 'Adjustment', 'Initial') NOT NULL,
        quantity_change DECIMAL(10, 2) NOT NULL,
        quantity_before DECIMAL(10, 2) NOT NULL,
        quantity_after DECIMAL(10, 2) NOT NULL,
        from_category VARCHAR(50) NULL,
        to_category VARCHAR(50) NULL,
        reason TEXT NULL,
        performed_by VARCHAR(100) NULL,
        movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stock_item_id) REFERENCES stock_items(id) ON DELETE CASCADE,
        INDEX idx_stock_item (stock_item_id),
        INDEX idx_movement_type (movement_type),
        INDEX idx_movement_date (movement_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(stock_movements_table)
        conn.commit()
        print("✓ stock_movements table created successfully")
    except Exception as e:
        print(f"✗ Error creating stock_movements table: {str(e)}")
        conn.rollback()
    
    # 3. Stock Alerts Table (for tracking low stock and expiry alerts)
    stock_alerts_table = """
    CREATE TABLE IF NOT EXISTS stock_alerts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        stock_item_id INT NOT NULL,
        alert_type ENUM('Low Stock', 'Expiring Soon', 'Expired') NOT NULL,
        threshold_value DECIMAL(10, 2) NULL,
        alert_message TEXT NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP NULL,
        FOREIGN KEY (stock_item_id) REFERENCES stock_items(id) ON DELETE CASCADE,
        INDEX idx_stock_item (stock_item_id),
        INDEX idx_alert_type (alert_type),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(stock_alerts_table)
        conn.commit()
        print("✓ stock_alerts table created successfully")
    except Exception as e:
        print(f"✗ Error creating stock_alerts table: {str(e)}")
        conn.rollback()
    
    # Verify tables
    print("\nVerifying tables...")
    cursor.execute("SHOW TABLES LIKE 'stock%'")
    tables = cursor.fetchall()
    
    if len(tables) >= 3:
        print(f"✓ All {len(tables)} warehouse tables created successfully\n")
        
        # Show table structures
        for table in tables:
            table_name = table[0]
            print(f"\n{table_name} structure:")
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
    
    cursor.close()
    conn.close()


def insert_sample_data():
    """Insert sample warehouse data for testing"""
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("Inserting sample warehouse data...")
    print("="*50 + "\n")
    
    sample_items = [
        # Feed items
        ("Cattle Feed Type A", "Feed", "B-1023", 1200, "kg", "2026-01-15", None),
        ("Layer Feed", "Feed", "B-2045", 100, "kg", "2026-03-20", None),
        ("Broiler Feed Mix", "Feed", "B-3067", 800, "kg", "2026-02-10", None),
        
        # Medicine items
        ("Antibiotic X", "Medicine", "M-0456", 25, "Vials", "2025-12-01", None),
        ("Vitamin B12", "Medicine", "M-1122", 15, "Vials", "2025-12-05", None),
        ("Deworming Tablets", "Medicine", "M-2233", 200, "Tablets", "2026-06-15", None),
        
        # Equipment items
        ("Milking Machine Parts", "Equipment", "E-5678", 5, "Pcs", None, None),
        ("Feed Storage Bins", "Equipment", "E-7890", 10, "Pcs", None, None),
        
        # Products
        ("Fresh Milk", "Products", "P-3451", 50, "L", "2025-11-28", None),
        ("Fresh Eggs", "Products", "P-3452", 1200, "Pcs", "2025-12-05", None),
    ]
    
    try:
        for item in sample_items:
            cursor.execute(
                """INSERT INTO stock_items 
                   (item_name, category, batch_no, quantity, unit, expiry_date, photo_path)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                item
            )
        
        conn.commit()
        print(f"✓ Successfully inserted {len(sample_items)} sample stock items")
        
        # Get inserted items to create initial movements
        cursor.execute("SELECT id, item_name, quantity FROM stock_items")
        items = cursor.fetchall()
        
        # Create initial stock movements
        for item in items:
            item_id, item_name, quantity = item
            cursor.execute(
                """INSERT INTO stock_movements
                   (stock_item_id, movement_type, quantity_change, quantity_before, quantity_after, reason)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (item_id, "Initial", quantity, 0, quantity, f"Initial stock entry for {item_name}")
            )
        
        conn.commit()
        print(f"✓ Successfully created {len(items)} initial stock movements")
        
    except Exception as e:
        print(f"✗ Error inserting sample data: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("="*50)
    print("WAREHOUSE DATABASE SETUP")
    print("="*50 + "\n")
    
    create_warehouse_tables()
    
    # Ask if user wants to insert sample data
    response = input("\nDo you want to insert sample data? (yes/no): ").lower().strip()
    if response in ['yes', 'y']:
        insert_sample_data()
    
    print("\n" + "="*50)
    print("Database setup completed!")
    print("="*50)
