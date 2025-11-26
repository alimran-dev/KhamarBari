"""
Database schema for farm calendar system
Creates tables for calendar events, reminders, and event management
"""

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def create_calendar_tables():
    """Creates all calendar-related tables"""
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )
    cursor = conn.cursor()
    
    print("Creating calendar tables...\n")
    
    # 1. Farm Events Table
    farm_events_table = """
    CREATE TABLE IF NOT EXISTS farm_events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(300) NOT NULL,
        event_type ENUM('Vaccination', 'Breeding', 'Vet Visit', 'Order', 'Labour', 'Feeding', 'Medication', 'Checkup', 'Other') NOT NULL,
        event_date DATE NOT NULL,
        event_time TIME NULL,
        end_date DATE NULL,
        end_time TIME NULL,
        all_day BOOLEAN DEFAULT FALSE,
        related_animals TEXT NULL COMMENT 'Comma-separated list of animal tags',
        assigned_person VARCHAR(200) NULL,
        location VARCHAR(300) NULL,
        notes TEXT,
        status ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
        color VARCHAR(50) NULL COMMENT 'Event color for calendar display',
        reminder_email BOOLEAN DEFAULT FALSE,
        reminder_sms BOOLEAN DEFAULT FALSE,
        reminder_time INT NULL COMMENT 'Minutes before event',
        created_by VARCHAR(100) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_event_date (event_date),
        INDEX idx_event_type (event_type),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(farm_events_table)
        conn.commit()
        print("✓ farm_events table created successfully")
    except Exception as e:
        print(f"✗ Error creating farm_events table: {str(e)}")
        conn.rollback()
    
    # 2. Event Reminders Table
    event_reminders_table = """
    CREATE TABLE IF NOT EXISTS event_reminders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event_id INT NOT NULL,
        reminder_type ENUM('Email', 'SMS', 'Notification') NOT NULL,
        reminder_time DATETIME NOT NULL,
        sent BOOLEAN DEFAULT FALSE,
        sent_at TIMESTAMP NULL,
        recipient VARCHAR(200) NULL,
        FOREIGN KEY (event_id) REFERENCES farm_events(id) ON DELETE CASCADE,
        INDEX idx_event_id (event_id),
        INDEX idx_reminder_time (reminder_time),
        INDEX idx_sent (sent)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(event_reminders_table)
        conn.commit()
        print("✓ event_reminders table created successfully")
    except Exception as e:
        print(f"✗ Error creating event_reminders table: {str(e)}")
        conn.rollback()
    
    # 3. Recurring Events Table
    recurring_events_table = """
    CREATE TABLE IF NOT EXISTS recurring_events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event_id INT NOT NULL,
        recurrence_type ENUM('Daily', 'Weekly', 'Monthly', 'Yearly') NOT NULL,
        recurrence_interval INT DEFAULT 1,
        recurrence_end_date DATE NULL,
        recurrence_count INT NULL,
        days_of_week VARCHAR(20) NULL COMMENT 'Comma-separated days: Mon,Wed,Fri',
        day_of_month INT NULL,
        FOREIGN KEY (event_id) REFERENCES farm_events(id) ON DELETE CASCADE,
        INDEX idx_event_id (event_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(recurring_events_table)
        conn.commit()
        print("✓ recurring_events table created successfully")
    except Exception as e:
        print(f"✗ Error creating recurring_events table: {str(e)}")
        conn.rollback()
    
    # 4. Event Attachments Table
    event_attachments_table = """
    CREATE TABLE IF NOT EXISTS event_attachments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event_id INT NOT NULL,
        file_name VARCHAR(300) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_type VARCHAR(50) NULL,
        file_size INT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES farm_events(id) ON DELETE CASCADE,
        INDEX idx_event_id (event_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(event_attachments_table)
        conn.commit()
        print("✓ event_attachments table created successfully")
    except Exception as e:
        print(f"✗ Error creating event_attachments table: {str(e)}")
        conn.rollback()
    
    cursor.close()
    conn.close()
    
    print("\n✓ All calendar tables created successfully!")
    return True


def insert_sample_events():
    """Insert some sample events for testing"""
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )
    cursor = conn.cursor()
    
    sample_events = [
        ("Vaccination - Herd A", "Vaccination", "2025-11-23", "10:00:00", None, "Annual FMD vaccination for Herd A", "Scheduled"),
        ("Vet Visit - Dr. Rahim", "Vet Visit", "2025-11-26", "14:00:00", "C-20512", "Routine checkup", "Scheduled"),
        ("Breeding - C-20512", "Breeding", "2025-11-21", None, "C-20512", "Scheduled breeding", "Completed"),
        ("Order Delivery - #ORD-00124", "Order", "2025-11-29", "09:00:00", None, "Customer order delivery", "Scheduled"),
    ]
    
    try:
        for event in sample_events:
            cursor.execute("""
                INSERT INTO farm_events 
                (title, event_type, event_date, event_time, related_animals, notes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, event)
        
        conn.commit()
        print("✓ Sample events inserted successfully")
    except Exception as e:
        print(f"✗ Error inserting sample events: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Farm Calendar Database Setup")
    print("=" * 60)
    
    create_calendar_tables()
    insert_sample_events()
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
