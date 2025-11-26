"""
Migration script to fix financial_entries table to use email instead of user_id
"""

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def migrate_financial_entries():
    """Migrate financial_entries table to use user_email instead of user_id"""
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Finance Module - Database Migration                   ║")
    print("║   Changing user_id to user_email                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "khamarbari")
        )
        cursor = conn.cursor()
        
        print("Step 1: Checking if migration is needed...")
        
        # Check if user_email column exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
            AND table_name = 'financial_entries'
            AND column_name = 'user_email'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("  ✓ user_email column already exists. Migration not needed.")
            cursor.close()
            conn.close()
            return True
        
        print("  ⚠ user_email column doesn't exist. Starting migration...")
        
        # Step 1: Add user_email column
        print("\nStep 2: Adding user_email column...")
        cursor.execute("""
            ALTER TABLE financial_entries
            ADD COLUMN user_email VARCHAR(255) NULL AFTER id
        """)
        conn.commit()
        print("  ✓ user_email column added")
        
        # Step 2: Check if there's any data to migrate
        print("\nStep 3: Checking for existing data...")
        cursor.execute("SELECT COUNT(*) FROM financial_entries")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"  ⚠ Found {count} existing entries")
            print("  ⚠ Cannot automatically migrate because users table uses email as PK")
            print("  ℹ All existing entries will need to be manually updated or deleted")
            print("\n  Would you like to:")
            print("    1. Delete all existing entries (start fresh)")
            print("    2. Keep them (you'll need to manually update user_email)")
            print("    3. Cancel migration")
            
            choice = input("\n  Enter your choice (1/2/3): ").strip()
            
            if choice == "1":
                cursor.execute("DELETE FROM financial_entries")
                conn.commit()
                print(f"  ✓ Deleted {cursor.rowcount} entries")
            elif choice == "2":
                print("  ℹ Keeping existing entries. Please update user_email manually.")
            else:
                print("  ✗ Migration cancelled")
                cursor.execute("ALTER TABLE financial_entries DROP COLUMN user_email")
                conn.commit()
                cursor.close()
                conn.close()
                return False
        else:
            print("  ✓ No existing entries to migrate")
        
        # Step 3: Make user_email NOT NULL and add index
        print("\nStep 4: Setting user_email as NOT NULL and adding index...")
        cursor.execute("""
            ALTER TABLE financial_entries
            MODIFY COLUMN user_email VARCHAR(255) NOT NULL
        """)
        cursor.execute("""
            CREATE INDEX idx_user_email ON financial_entries(user_email)
        """)
        conn.commit()
        print("  ✓ user_email is now NOT NULL with index")
        
        # Step 4: Drop old user_id column if it exists
        print("\nStep 5: Checking for old user_id column...")
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
            AND table_name = 'financial_entries'
            AND column_name = 'user_id'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("  ⚠ Dropping old user_id column...")
            # First drop the index
            try:
                cursor.execute("DROP INDEX idx_user_id ON financial_entries")
            except:
                pass  # Index might not exist
            
            cursor.execute("""
                ALTER TABLE financial_entries
                DROP COLUMN user_id
            """)
            conn.commit()
            print("  ✓ user_id column removed")
        else:
            print("  ✓ user_id column doesn't exist (already using user_email)")
        
        # Step 5: Show final structure
        print("\nStep 6: Verifying final structure...")
        cursor.execute("DESCRIBE financial_entries")
        columns = cursor.fetchall()
        print("\n  Final table structure:")
        for col in columns:
            print(f"    - {col[0]}: {col[1]} {'NOT NULL' if col[2] == 'NO' else 'NULL'}")
        
        cursor.close()
        conn.close()
        
        print("\n╔══════════════════════════════════════════════════════════╗")
        print("║              ✅ Migration Completed!                     ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print("\n✓ financial_entries table now uses user_email")
        print("✓ Ready to use finance module")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"\n✗ Database Error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    migrate_financial_entries()
