import mysql.connector
from config.db import get_connection

def init_db():
    """Initialize the database with necessary tables if they don't exist."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Checking and initializing database tables...")
        
        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
              owner_name VARCHAR(30) DEFAULT NULL,
              farm_name VARCHAR(30) DEFAULT NULL,
              phone_number VARCHAR(11) DEFAULT NULL,
              email VARCHAR(30) NOT NULL,
              password VARCHAR(30) DEFAULT NULL,
              photo_url VARCHAR(255) DEFAULT NULL,
              PRIMARY KEY (email)
            )
        """)
        
        # 2. Cattles Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cattles (
              id INT AUTO_INCREMENT PRIMARY KEY,
              Name VARCHAR(255) NOT NULL,
              weight FLOAT,
              tag_number VARCHAR(50),
              breed VARCHAR(50),
              purpose VARCHAR(50),
              gender VARCHAR(20),
              dob DATE,
              entry_date DATE,
              initial_weight FLOAT,
              current_weight FLOAT,
              health_notes TEXT,
              medical_history TEXT,
              seller_name VARCHAR(100),
              seller_address VARCHAR(255),
              seller_phone VARCHAR(20),
              photo_path VARCHAR(255),
              documents_path VARCHAR(255),
              is_archived BOOLEAN DEFAULT FALSE,
              user_email VARCHAR(255),
              UNIQUE KEY tag_number (tag_number),
              INDEX idx_user_email (user_email)
            )
        """)
        
        # 3. Medical History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_history (
              id INT AUTO_INCREMENT PRIMARY KEY,
              cattle_id INT NOT NULL,
              date DATE,
              name VARCHAR(255),
              diagnosis TEXT,
              FOREIGN KEY (cattle_id) REFERENCES cattles(id) ON DELETE CASCADE,
              INDEX idx_cattle_id (cattle_id)
            )
        """)
        
        # 4. Production Entries Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_entries (
              id INT AUTO_INCREMENT PRIMARY KEY,
              cattle_id INT NOT NULL,
              animal_tag VARCHAR(50) NOT NULL,
              animal_name VARCHAR(100),
              product_type ENUM('Milk','Eggs','Wool bale','Waste bin') NOT NULL,
              quantity DECIMAL(10,2) NOT NULL,
              unit VARCHAR(20) NOT NULL,
              entry_time VARCHAR(20) NOT NULL,
              entry_date VARCHAR(20) NOT NULL,
              notes TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              reserved_quantity DECIMAL(10,2) DEFAULT 0.00,
              FOREIGN KEY (cattle_id) REFERENCES cattles(id) ON DELETE CASCADE,
              INDEX idx_animal_tag (animal_tag),
              INDEX idx_entry_date (entry_date),
              INDEX idx_product_type (product_type)
            )
        """)
        
        # 5. Orders Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
              id INT AUTO_INCREMENT PRIMARY KEY,
              order_id VARCHAR(50) NOT NULL,
              customer_name VARCHAR(255) NOT NULL,
              customer_email VARCHAR(255),
              customer_phone VARCHAR(20),
              total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
              delivery_date DATE,
              status ENUM('Pending','Pre Order','Packed','Out for Delivery','Delivered','Cancelled') DEFAULT 'Pending',
              notes TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              packed_at TIMESTAMP NULL,
              out_for_delivery_at TIMESTAMP NULL,
              delivered_at TIMESTAMP NULL,
              UNIQUE KEY order_id (order_id),
              INDEX idx_order_id (order_id),
              INDEX idx_customer_name (customer_name),
              INDEX idx_status (status),
              INDEX idx_created_at (created_at)
            )
        """)
        
        # 6. Order Items Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
              id INT AUTO_INCREMENT PRIMARY KEY,
              order_id VARCHAR(50) NOT NULL,
              product_type VARCHAR(100) NOT NULL,
              quantity DECIMAL(10,2) NOT NULL,
              unit VARCHAR(50),
              price_per_unit DECIMAL(10,2) DEFAULT 0.00,
              notes TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
              INDEX idx_order_id (order_id),
              INDEX idx_product_type (product_type)
            )
        """)
        
        # 7. Labourers Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labourers (
              id INT AUTO_INCREMENT PRIMARY KEY,
              full_name VARCHAR(255) NOT NULL,
              phone_number VARCHAR(20),
              national_id VARCHAR(50),
              address TEXT,
              photo_url VARCHAR(500),
              position VARCHAR(100) NOT NULL,
              joining_date DATE NOT NULL,
              status ENUM('Active','Inactive') DEFAULT 'Active',
              pay_type ENUM('Monthly_Salary','Daily_Wage') NOT NULL,
              base_rate DECIMAL(10,2) NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              UNIQUE KEY national_id (national_id),
              INDEX idx_full_name (full_name),
              INDEX idx_status (status),
              INDEX idx_position (position),
              INDEX idx_pay_type (pay_type)
            )
        """)
        
        # 8. Attendance Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
              id INT AUTO_INCREMENT PRIMARY KEY,
              labour_id INT NOT NULL,
              date DATE NOT NULL,
              status ENUM('Present','Absent','Half-Day') NOT NULL,
              overtime_hours INT DEFAULT 0,
              notes TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              UNIQUE KEY unique_attendance (labour_id, date),
              FOREIGN KEY (labour_id) REFERENCES labourers(id) ON DELETE CASCADE,
              INDEX idx_labour_date (labour_id, date),
              INDEX idx_date (date),
              INDEX idx_status (status)
            )
        """)
        
        # 9. Payroll Transactions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payroll_transactions (
              id INT AUTO_INCREMENT PRIMARY KEY,
              labour_id INT NOT NULL,
              month INT NOT NULL,
              year INT NOT NULL,
              total_working_days DECIMAL(5,1) NOT NULL,
              base_earning DECIMAL(10,2) NOT NULL,
              bonus_amount DECIMAL(10,2) DEFAULT 0.00,
              deduction_amount DECIMAL(10,2) DEFAULT 0.00,
              total_payable DECIMAL(10,2) NOT NULL,
              payment_status ENUM('Pending','Paid') DEFAULT 'Pending',
              payment_date DATE,
              notes TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              UNIQUE KEY unique_payroll (labour_id, month, year),
              FOREIGN KEY (labour_id) REFERENCES labourers(id) ON DELETE CASCADE,
              INDEX idx_labour_month_year (labour_id, month, year),
              INDEX idx_payment_status (payment_status),
              INDEX idx_year_month (year, month)
            )
        """)
        
        # 10. Stock Items Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_items (
              id INT AUTO_INCREMENT PRIMARY KEY,
              item_name VARCHAR(200) NOT NULL,
              category ENUM('Feed','Medicine','Equipment','Products') NOT NULL,
              batch_no VARCHAR(100) NOT NULL,
              quantity DECIMAL(10,2) NOT NULL DEFAULT 0.00,
              unit VARCHAR(50) NOT NULL,
              expiry_date DATE,
              photo_path VARCHAR(500),
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              INDEX idx_category (category),
              INDEX idx_batch_no (batch_no),
              INDEX idx_expiry_date (expiry_date),
              INDEX idx_item_name (item_name)
            )
        """)
        
        # 11. Stock Movements Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
              id INT AUTO_INCREMENT PRIMARY KEY,
              stock_item_id INT NOT NULL,
              movement_type ENUM('Add','Remove','Transfer','Adjustment','Initial') NOT NULL,
              quantity_change DECIMAL(10,2) NOT NULL,
              quantity_before DECIMAL(10,2) NOT NULL,
              quantity_after DECIMAL(10,2) NOT NULL,
              from_category VARCHAR(50),
              to_category VARCHAR(50),
              reason TEXT,
              performed_by VARCHAR(100),
              movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (stock_item_id) REFERENCES stock_items(id) ON DELETE CASCADE,
              INDEX idx_stock_item (stock_item_id),
              INDEX idx_movement_type (movement_type),
              INDEX idx_movement_date (movement_date)
            )
        """)
        
        # 12. Financial Entries Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_entries (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_email VARCHAR(255) NOT NULL,
              entry_type ENUM('expense','income') NOT NULL,
              category_id INT NOT NULL,
              amount DECIMAL(12,2) NOT NULL,
              date DATE NOT NULL,
              description TEXT,
              notes TEXT,
              receipt_path VARCHAR(500),
              linked_item_type VARCHAR(50) COMMENT 'animal, product, order, labour',
              linked_item_id INT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              FOREIGN KEY (category_id) REFERENCES financial_categories(id) ON DELETE RESTRICT,
              INDEX idx_entry_type (entry_type),
              INDEX idx_category_id (category_id),
              INDEX idx_date (date),
              INDEX idx_linked_item (linked_item_type, linked_item_id),
              INDEX idx_user_email (user_email)
            )
        """)
        
        # 13. Farm Events Table (Calendar)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farm_events (
              id INT AUTO_INCREMENT PRIMARY KEY,
              title VARCHAR(300) NOT NULL,
              event_type ENUM('Vaccination','Breeding','Vet Visit','Order','Labour','Feeding','Medication','Checkup','Other') NOT NULL,
              event_date DATE NOT NULL,
              event_time TIME,
              end_date DATE,
              end_time TIME,
              all_day BOOLEAN DEFAULT FALSE,
              related_animals TEXT COMMENT 'Comma-separated list of animal tags',
              assigned_person VARCHAR(200),
              location VARCHAR(300),
              notes TEXT,
              status ENUM('Scheduled','In Progress','Completed','Cancelled') DEFAULT 'Scheduled',
              color VARCHAR(50) COMMENT 'Event color for calendar display',
              reminder_email BOOLEAN DEFAULT FALSE,
              reminder_sms BOOLEAN DEFAULT FALSE,
              reminder_time INT COMMENT 'Minutes before event',
              created_by VARCHAR(100),
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              INDEX idx_event_date (event_date),
              INDEX idx_event_type (event_type),
              INDEX idx_status (status)
            )
        """)

        # 14. Financial Categories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_categories (
              id INT AUTO_INCREMENT PRIMARY KEY,
              name VARCHAR(100) NOT NULL UNIQUE,
              type ENUM('expense','income') NOT NULL,
              description TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_type (type)
            )
        """)

        # 15. Expense Templates Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_templates (
              id INT AUTO_INCREMENT PRIMARY KEY,
              name VARCHAR(100) NOT NULL,
              category_id INT NOT NULL,
              default_amount DECIMAL(12,2),
              description TEXT,
              icon VARCHAR(50),
              is_active BOOLEAN DEFAULT TRUE,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (category_id) REFERENCES financial_categories(id) ON DELETE CASCADE,
              INDEX idx_category_id (category_id)
            )
        """)

        # 16. Common Diseases Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS common_diseases (
              id INT AUTO_INCREMENT PRIMARY KEY,
              disease_name VARCHAR(300) NOT NULL,
              category VARCHAR(100),
              symptoms TEXT,
              common_treatment TEXT,
              prevention TEXT,
              severity ENUM('Low','Medium','High','Critical') DEFAULT 'Medium',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_disease_name (disease_name),
              INDEX idx_category (category)
            )
        """)

        # 17. Veterinary Visits Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veterinary_visits (
              id INT AUTO_INCREMENT PRIMARY KEY,
              animal_tag VARCHAR(100) NOT NULL,
              animal_name VARCHAR(200),
              visit_date DATE NOT NULL,
              visit_type ENUM('Routine Check','Emergency','Follow-up','Vaccination','Surgery') NOT NULL DEFAULT 'Routine Check',
              vet_name VARCHAR(200) NOT NULL,
              diagnosis TEXT,
              treatment TEXT,
              medicines_used TEXT,
              cost DECIMAL(10,2) DEFAULT 0.00,
              notes TEXT,
              next_visit_date DATE,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              INDEX idx_animal_tag (animal_tag),
              INDEX idx_visit_date (visit_date),
              INDEX idx_visit_type (visit_type)
            )
        """)

        # 18. Veterinary Treatments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veterinary_treatments (
              id INT AUTO_INCREMENT PRIMARY KEY,
              visit_id INT,
              animal_tag VARCHAR(100) NOT NULL,
              treatment_date DATE NOT NULL,
              diagnosis VARCHAR(500),
              treatment_description TEXT NOT NULL,
              medicines_used TEXT,
              dosage VARCHAR(200),
              duration_days INT,
              cost DECIMAL(10,2) DEFAULT 0.00,
              vet_name VARCHAR(200),
              notes TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              FOREIGN KEY (visit_id) REFERENCES veterinary_visits(id) ON DELETE SET NULL,
              INDEX idx_animal_tag (animal_tag),
              INDEX idx_treatment_date (treatment_date),
              INDEX idx_visit_id (visit_id)
            )
        """)

        # 19. Veterinary Reports Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veterinary_reports (
              id INT AUTO_INCREMENT PRIMARY KEY,
              visit_id INT,
              animal_tag VARCHAR(100) NOT NULL,
              report_date DATE NOT NULL,
              report_type VARCHAR(100),
              file_path VARCHAR(500),
              file_name VARCHAR(300),
              description TEXT,
              uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (visit_id) REFERENCES veterinary_visits(id) ON DELETE SET NULL,
              INDEX idx_animal_tag (animal_tag),
              INDEX idx_report_date (report_date),
              INDEX idx_visit_id (visit_id)
            )
        """)

        # 20. Vaccination Schedule Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vaccination_schedule (
              id INT AUTO_INCREMENT PRIMARY KEY,
              animal_tag VARCHAR(100) NOT NULL,
              animal_name VARCHAR(200),
              vaccine_name VARCHAR(300) NOT NULL,
              scheduled_date DATE NOT NULL,
              completed BOOLEAN DEFAULT FALSE,
              completion_date DATE,
              vet_name VARCHAR(200),
              cost DECIMAL(10,2) DEFAULT 0.00,
              notes TEXT,
              reminder_sent BOOLEAN DEFAULT FALSE,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              INDEX idx_animal_tag (animal_tag),
              INDEX idx_scheduled_date (scheduled_date),
              INDEX idx_completed (completed)
            )
        """)

        # 21. Medical History Detailed Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_history_detailed (
              id INT AUTO_INCREMENT PRIMARY KEY,
              animal_tag VARCHAR(100) NOT NULL,
              animal_name VARCHAR(200),
              date DATE NOT NULL,
              record_type ENUM('Vaccination','Treatment','Surgery','Checkup','Disease','Injury','Other') NOT NULL,
              disease_name VARCHAR(300),
              diagnosis TEXT,
              treatment TEXT,
              medicines_used TEXT,
              vet_name VARCHAR(200),
              cost DECIMAL(10,2) DEFAULT 0.00,
              notes TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              INDEX idx_animal_tag (animal_tag),
              INDEX idx_date (date),
              INDEX idx_record_type (record_type)
            )
        """)

        # 22. Stock Alerts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_alerts (
              id INT AUTO_INCREMENT PRIMARY KEY,
              stock_item_id INT NOT NULL,
              alert_type ENUM('Low Stock','Expiring Soon','Expired') NOT NULL,
              threshold_value DECIMAL(10,2),
              alert_message TEXT NOT NULL,
              is_active BOOLEAN DEFAULT TRUE,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              resolved_at TIMESTAMP,
              FOREIGN KEY (stock_item_id) REFERENCES stock_items(id) ON DELETE CASCADE,
              INDEX idx_stock_item (stock_item_id),
              INDEX idx_alert_type (alert_type),
              INDEX idx_is_active (is_active)
            )
        """)

        # 23. Event Attachments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_attachments (
              id INT AUTO_INCREMENT PRIMARY KEY,
              event_id INT NOT NULL,
              file_name VARCHAR(300) NOT NULL,
              file_path VARCHAR(500) NOT NULL,
              file_type VARCHAR(50),
              file_size INT,
              uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (event_id) REFERENCES farm_events(id) ON DELETE CASCADE,
              INDEX idx_event_id (event_id)
            )
        """)

        # 24. Event Reminders Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_reminders (
              id INT AUTO_INCREMENT PRIMARY KEY,
              event_id INT NOT NULL,
              reminder_type ENUM('Email','SMS','Notification') NOT NULL,
              reminder_time DATETIME NOT NULL,
              sent BOOLEAN DEFAULT FALSE,
              sent_at TIMESTAMP,
              recipient VARCHAR(200),
              FOREIGN KEY (event_id) REFERENCES farm_events(id) ON DELETE CASCADE,
              INDEX idx_event_id (event_id),
              INDEX idx_reminder_time (reminder_time),
              INDEX idx_sent (sent)
            )
        """)

        # 25. Recurring Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring_events (
              id INT AUTO_INCREMENT PRIMARY KEY,
              event_id INT NOT NULL,
              recurrence_type ENUM('Daily','Weekly','Monthly','Yearly') NOT NULL,
              recurrence_interval INT DEFAULT 1,
              recurrence_end_date DATE,
              recurrence_count INT,
              days_of_week VARCHAR(20) COMMENT 'Comma-separated days: Mon,Wed,Fri',
              day_of_month INT,
              FOREIGN KEY (event_id) REFERENCES farm_events(id) ON DELETE CASCADE,
              INDEX idx_event_id (event_id)
            )
        """)
        
        print("Database initialization completed successfully.")
        conn.close()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
