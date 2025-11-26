"""
Database schema creation for Labour Management System
Run this script to create the labourers, attendance, and payroll_transactions tables
"""

from dotenv import load_dotenv
load_dotenv()

from config.db import get_connection

def create_labour_tables():
    """Creates the labour management tables if they don't exist."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("=" * 70)
        print("Creating Labour Management Tables")
        print("=" * 70)
        
        # Create labourers table
        print("\n1. Creating labourers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labourers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                phone_number VARCHAR(20),
                national_id VARCHAR(50) UNIQUE,
                address TEXT,
                photo_url VARCHAR(500),
                position VARCHAR(100) NOT NULL,
                joining_date DATE NOT NULL,
                status ENUM('Active', 'Inactive') DEFAULT 'Active',
                pay_type ENUM('Monthly_Salary', 'Daily_Wage') NOT NULL,
                base_rate DECIMAL(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_full_name (full_name),
                INDEX idx_status (status),
                INDEX idx_position (position),
                INDEX idx_pay_type (pay_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✓ Labourers table created successfully!")
        
        # Create attendance table
        print("\n2. Creating attendance table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                labour_id INT NOT NULL,
                date DATE NOT NULL,
                status ENUM('Present', 'Absent', 'Half-Day') NOT NULL,
                overtime_hours INT DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (labour_id) REFERENCES labourers(id) ON DELETE CASCADE,
                UNIQUE KEY unique_attendance (labour_id, date),
                INDEX idx_labour_date (labour_id, date),
                INDEX idx_date (date),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✓ Attendance table created successfully!")
        
        # Create payroll_transactions table
        print("\n3. Creating payroll_transactions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payroll_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                labour_id INT NOT NULL,
                month INT NOT NULL,
                year INT NOT NULL,
                total_working_days DECIMAL(5, 1) NOT NULL,
                base_earning DECIMAL(10, 2) NOT NULL,
                bonus_amount DECIMAL(10, 2) DEFAULT 0.00,
                deduction_amount DECIMAL(10, 2) DEFAULT 0.00,
                total_payable DECIMAL(10, 2) NOT NULL,
                payment_status ENUM('Pending', 'Paid') DEFAULT 'Pending',
                payment_date DATE NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (labour_id) REFERENCES labourers(id) ON DELETE CASCADE,
                UNIQUE KEY unique_payroll (labour_id, month, year),
                INDEX idx_labour_month_year (labour_id, month, year),
                INDEX idx_payment_status (payment_status),
                INDEX idx_year_month (year, month)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✓ Payroll_transactions table created successfully!")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ All Labour Management tables created successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        raise


if __name__ == "__main__":
    create_labour_tables()
