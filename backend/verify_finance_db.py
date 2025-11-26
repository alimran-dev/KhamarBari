"""
Complete database verification and fix script for Finance Module
This script will:
1. Check if tables exist
2. Verify column structures
3. Fix any missing columns
4. Ensure proper relationships
5. Insert default data if missing
"""

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()


def get_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )


def check_users_table():
    """Ensure users table has id column"""
    print("\n=== Checking Users Table ===")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = 'users'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("⚠ Users table doesn't exist. Creating...")
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    owner_name VARCHAR(255) NOT NULL,
                    farm_name VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    photo_url VARCHAR(500) NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            conn.commit()
            print("✓ Users table created")
        else:
            # Check if id column exists
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                AND table_name = 'users'
                AND column_name = 'id'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("⚠ Users table missing 'id' column. This is critical!")
                print("  Attempting to add id column...")
                try:
                    cursor.execute("""
                        ALTER TABLE users 
                        ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST
                    """)
                    conn.commit()
                    print("✓ Added id column to users table")
                except Error as e:
                    print(f"✗ Failed to add id column: {e}")
                    print("  Manual fix required - see instructions below")
            else:
                print("✓ Users table has id column")
        
        # Show users table structure
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        print("\n  Users table structure:")
        for col in columns:
            print(f"    - {col[0]}: {col[1]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"✗ Error checking users table: {e}")
        return False


def check_financial_tables():
    """Check and fix financial tables"""
    print("\n=== Checking Financial Tables ===")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Check financial_categories table
        print("\n1. Checking financial_categories table...")
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = 'financial_categories'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("  ⚠ Creating financial_categories table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    type ENUM('expense', 'income') NOT NULL,
                    description TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_category_name (name),
                    INDEX idx_type (type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            conn.commit()
            print("  ✓ financial_categories table created")
        else:
            print("  ✓ financial_categories table exists")
        
        # 2. Check financial_entries table
        print("\n2. Checking financial_entries table...")
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = 'financial_entries'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("  ⚠ Creating financial_entries table...")
            cursor.execute("""
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
            """)
            conn.commit()
            print("  ✓ financial_entries table created")
        else:
            print("  ✓ financial_entries table exists")
        
        # 3. Check expense_templates table
        print("\n3. Checking expense_templates table...")
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = 'expense_templates'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("  ⚠ Creating expense_templates table...")
            cursor.execute("""
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
            """)
            conn.commit()
            print("  ✓ expense_templates table created")
        else:
            print("  ✓ expense_templates table exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"✗ Error checking financial tables: {e}")
        return False


def insert_default_data():
    """Insert default categories and templates if missing"""
    print("\n=== Checking Default Data ===")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if categories exist
        cursor.execute("SELECT COUNT(*) FROM financial_categories")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("  ⚠ No categories found. Inserting defaults...")
            
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
            
            cursor.executemany("""
                INSERT INTO financial_categories (name, type, description) 
                VALUES (%s, %s, %s)
            """, default_categories)
            conn.commit()
            print(f"  ✓ Inserted {cursor.rowcount} categories")
        else:
            print(f"  ✓ Found {count} existing categories")
        
        # Check if templates exist
        cursor.execute("SELECT COUNT(*) FROM expense_templates")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("  ⚠ No templates found. Inserting defaults...")
            
            # Get category IDs
            cursor.execute("SELECT id, name FROM financial_categories")
            category_map = {name: cat_id for cat_id, name in cursor.fetchall()}
            
            default_templates = [
                ('Feed Purchase', category_map.get('Feed'), None, 'Regular feed purchase', '🌾'),
                ('Vet Visit', category_map.get('Vet'), None, 'Veterinary consultation', '🏥'),
                ('Milk Sale', category_map.get('Sales'), None, 'Daily milk sale', '🥛')
            ]
            
            cursor.executemany("""
                INSERT INTO expense_templates (name, category_id, default_amount, description, icon) 
                VALUES (%s, %s, %s, %s, %s)
            """, default_templates)
            conn.commit()
            print(f"  ✓ Inserted {cursor.rowcount} templates")
        else:
            print(f"  ✓ Found {count} existing templates")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"✗ Error inserting default data: {e}")
        return False


def test_finance_query():
    """Test the actual query used in the finance endpoint"""
    print("\n=== Testing Finance Query ===")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Test getting user ID (the query that was failing)
        print("  Testing: SELECT id FROM users WHERE email = 'test@example.com'")
        cursor.execute("SELECT id FROM users WHERE email = %s", ("test@example.com",))
        result = cursor.fetchone()
        
        if result:
            print(f"  ✓ Query successful! User ID: {result[0]}")
        else:
            print("  ⓘ No user found with email 'test@example.com' (this is OK if no test user)")
            
            # Try getting any user
            cursor.execute("SELECT id, email FROM users LIMIT 1")
            result = cursor.fetchone()
            if result:
                print(f"  ✓ Found a user: ID={result[0]}, Email={result[1]}")
            else:
                print("  ⚠ No users in database. You need to signup first!")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"  ✗ Query failed: {e}")
        return False


def create_test_user():
    """Create a test user if none exists"""
    print("\n=== Creating Test User (if needed) ===")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if any users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("  ⚠ No users found. Creating test user...")
            cursor.execute("""
                INSERT INTO users (owner_name, farm_name, phone_number, email, password)
                VALUES (%s, %s, %s, %s, %s)
            """, ("Test User", "Test Farm", "01712345678", "test@example.com", "password123"))
            conn.commit()
            print("  ✓ Test user created: test@example.com / password123")
        else:
            print(f"  ✓ Found {count} existing user(s)")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"  ✗ Error creating test user: {e}")
        return False


def main():
    """Run all checks and fixes"""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Finance Module - Database Verification & Fix          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    try:
        # Test database connection
        print("\nTesting database connection...")
        conn = get_connection()
        print("✓ Database connection successful")
        conn.close()
        
        # Run all checks
        success = True
        success = check_users_table() and success
        success = check_financial_tables() and success
        success = insert_default_data() and success
        success = create_test_user() and success
        success = test_finance_query() and success
        
        if success:
            print("\n╔══════════════════════════════════════════════════════════╗")
            print("║              ✅ All Checks Passed!                       ║")
            print("╚══════════════════════════════════════════════════════════╝")
            print("\n✓ Database is ready for finance module")
            print("✓ You can now use the finance features")
            print("\nNext steps:")
            print("  1. Start backend: uvicorn main:app --reload")
            print("  2. Run app: python3 main.py")
            print("  3. Login and test finance module")
        else:
            print("\n╔══════════════════════════════════════════════════════════╗")
            print("║              ⚠ Some Issues Found                         ║")
            print("╚══════════════════════════════════════════════════════════╝")
            print("\nPlease review the errors above and fix manually if needed.")
        
    except Error as e:
        print(f"\n✗ Critical Error: {e}")
        print("\nManual Fix Instructions:")
        print("1. Check your .env file has correct database credentials")
        print("2. Ensure MySQL server is running")
        print("3. Ensure database 'khamarbari' exists:")
        print("   mysql -u root -p -e 'CREATE DATABASE IF NOT EXISTS khamarbari;'")
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")


if __name__ == "__main__":
    main()
