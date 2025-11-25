"""
Script to create orders and order_items tables in the database.
Run this script once to set up the orders system tables.
"""

from config.db import get_connection

def create_orders_tables():
    """Creates the orders and order_items tables if they don't exist."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Creating orders table...")
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id VARCHAR(50) UNIQUE NOT NULL,
                customer_name VARCHAR(255) NOT NULL,
                customer_email VARCHAR(255),
                customer_phone VARCHAR(20),
                total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                delivery_date DATE,
                status ENUM('Pending', 'Pre Order', 'Packed', 'Out for Delivery', 'Delivered', 'Cancelled') DEFAULT 'Pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                packed_at TIMESTAMP NULL,
                out_for_delivery_at TIMESTAMP NULL,
                delivered_at TIMESTAMP NULL,
                INDEX idx_order_id (order_id),
                INDEX idx_customer_name (customer_name),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        print("Orders table created successfully!")
        
        print("Creating order_items table...")
        
        # Create order_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id VARCHAR(50) NOT NULL,
                product_type VARCHAR(100) NOT NULL,
                quantity DECIMAL(10, 2) NOT NULL,
                unit VARCHAR(50),
                price_per_unit DECIMAL(10, 2) DEFAULT 0.00,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                INDEX idx_order_id (order_id),
                INDEX idx_product_type (product_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        print("Order_items table created successfully!")
        
        print("Adding reserved_quantity column to production_entries...")
        
        # Check if column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'production_entries' 
            AND COLUMN_NAME = 'reserved_quantity'
        """)
        
        exists = cursor.fetchone()[0]
        
        if not exists:
            cursor.execute("""
                ALTER TABLE production_entries 
                ADD COLUMN reserved_quantity DECIMAL(10, 2) DEFAULT 0.00
            """)
            print("Reserved_quantity column added successfully!")
        else:
            print("Reserved_quantity column already exists!")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ All tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Creating Orders System Tables")
    print("=" * 60)
    create_orders_tables()
