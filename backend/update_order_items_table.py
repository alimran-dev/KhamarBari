"""
Script to update order_items table to add price_per_unit column.
Run this once to update the existing database schema.
"""

from config.db import get_connection

def update_order_items_table():
    """Add price_per_unit column to order_items table if it doesn't exist."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Updating order_items table...")
        
        # Add price_per_unit column
        try:
            cursor.execute("""
                ALTER TABLE order_items 
                ADD COLUMN price_per_unit DECIMAL(10, 2) DEFAULT 0.00 AFTER unit
            """)
            print("✅ Added price_per_unit column to order_items table")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ️  Column price_per_unit already exists")
            else:
                raise e
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating table: {e}")
        raise


if __name__ == "__main__":
    print("="*60)
    print("Updating Order Items Table Schema")
    print("="*60)
    update_order_items_table()
