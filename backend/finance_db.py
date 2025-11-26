"""
Database schema for financial tracking system
Creates tables for income/expense entries with receipts and linked items
"""

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def create_finance_tables():
    """Creates all finance-related tables"""
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )
    cursor = conn.cursor()
    
    print("Creating finance tables...\n")
    
    # 1. Financial Categories Table
    categories_table = """
    CREATE TABLE IF NOT EXISTS financial_categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        type ENUM('expense', 'income') NOT NULL,
        description TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_category_name (name),
        INDEX idx_type (type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(categories_table)
        conn.commit()
        print("✓ financial_categories table created successfully")
    except Exception as e:
        print(f"✗ Error creating financial_categories table: {e}")
        conn.rollback()
    
    # 2. Financial Entries Table
    entries_table = """
    CREATE TABLE IF NOT EXISTS financial_entries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        entry_type ENUM('expense', 'income') NOT NULL,
        category_id INT NOT NULL,
        amount DECIMAL(12, 2) NOT NULL,
        date DATE NOT NULL,
        description TEXT NULL,
        notes TEXT NULL,
        receipt_path VARCHAR(500) NULL,
        linked_item_type VARCHAR(50) NULL COMMENT 'animal, product, order, labour',
        linked_item_id INT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_entry_type (entry_type),
        INDEX idx_category_id (category_id),
        INDEX idx_date (date),
        INDEX idx_linked_item (linked_item_type, linked_item_id),
        FOREIGN KEY (category_id) REFERENCES financial_categories(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(entries_table)
        conn.commit()
        print("✓ financial_entries table created successfully")
    except Exception as e:
        print(f"✗ Error creating financial_entries table: {e}")
        conn.rollback()
    
    # 3. Expense Templates Table (for quick shortcuts)
    templates_table = """
    CREATE TABLE IF NOT EXISTS expense_templates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        category_id INT NOT NULL,
        default_amount DECIMAL(12, 2) NULL,
        description TEXT NULL,
        icon VARCHAR(50) NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_category_id (category_id),
        FOREIGN KEY (category_id) REFERENCES financial_categories(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(templates_table)
        conn.commit()
        print("✓ expense_templates table created successfully")
    except Exception as e:
        print(f"✗ Error creating expense_templates table: {e}")
        conn.rollback()
    
    # Insert default categories
    default_categories = [
        ('Feed', 'expense', 'Animal feed and fodder expenses'),
        ('Vet', 'expense', 'Veterinary and medical expenses'),
        ('Maintenance', 'expense', 'Farm maintenance and repairs'),
        ('Labor', 'expense', 'Labour wages and payments'),
        ('Other Expense', 'expense', 'Miscellaneous expenses'),
        ('Sales', 'income', 'Product sales revenue'),
        ('Livestock Sale', 'income', 'Animal sales revenue'),
        ('Other Income', 'income', 'Miscellaneous income')
    ]
    
    insert_category = """
    INSERT IGNORE INTO financial_categories (name, type, description) 
    VALUES (%s, %s, %s)
    """
    
    try:
        cursor.executemany(insert_category, default_categories)
        conn.commit()
        print(f"✓ Inserted {cursor.rowcount} default categories")
    except Exception as e:
        print(f"✗ Error inserting default categories: {e}")
        conn.rollback()
    
    # Insert default expense templates
    # First get category IDs
    cursor.execute("SELECT id, name FROM financial_categories")
    category_map = {name: cat_id for cat_id, name in cursor.fetchall()}
    
    default_templates = [
        ('Feed Purchase', category_map.get('Feed'), None, 'Regular feed purchase', '🌾'),
        ('Vet Visit', category_map.get('Vet'), None, 'Veterinary consultation', '🏥'),
        ('Milk Sale', category_map.get('Sales'), None, 'Daily milk sale', '🥛')
    ]
    
    insert_template = """
    INSERT IGNORE INTO expense_templates (name, category_id, default_amount, description, icon) 
    VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(insert_template, default_templates)
        conn.commit()
        print(f"✓ Inserted {cursor.rowcount} default templates")
    except Exception as e:
        print(f"✗ Error inserting default templates: {e}")
        conn.rollback()
    
    cursor.close()
    conn.close()
    
    print("\n✅ Finance database setup complete!")


if __name__ == "__main__":
    create_finance_tables()
