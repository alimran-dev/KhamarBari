"""
Database schema for veterinary management system
Creates tables for veterinary visits, treatments, medical history, and vaccination schedules
"""

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def create_veterinary_tables():
    """Creates all veterinary-related tables"""
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )
    cursor = conn.cursor()
    
    print("Creating veterinary tables...\n")
    
    # 1. Veterinary Visits Table
    veterinary_visits_table = """
    CREATE TABLE IF NOT EXISTS veterinary_visits (
        id INT AUTO_INCREMENT PRIMARY KEY,
        animal_tag VARCHAR(100) NOT NULL,
        animal_name VARCHAR(200),
        visit_date DATE NOT NULL,
        visit_type ENUM('Routine Check', 'Emergency', 'Follow-up', 'Vaccination', 'Surgery') NOT NULL DEFAULT 'Routine Check',
        vet_name VARCHAR(200) NOT NULL,
        diagnosis TEXT,
        treatment TEXT,
        medicines_used TEXT,
        cost DECIMAL(10, 2) DEFAULT 0.00,
        notes TEXT,
        next_visit_date DATE NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_animal_tag (animal_tag),
        INDEX idx_visit_date (visit_date),
        INDEX idx_visit_type (visit_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(veterinary_visits_table)
        conn.commit()
        print("✓ veterinary_visits table created successfully")
    except Exception as e:
        print(f"✗ Error creating veterinary_visits table: {str(e)}")
        conn.rollback()
    
    # 2. Veterinary Treatments Table
    veterinary_treatments_table = """
    CREATE TABLE IF NOT EXISTS veterinary_treatments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        visit_id INT NULL,
        animal_tag VARCHAR(100) NOT NULL,
        treatment_date DATE NOT NULL,
        diagnosis VARCHAR(500),
        treatment_description TEXT NOT NULL,
        medicines_used TEXT,
        dosage VARCHAR(200),
        duration_days INT,
        cost DECIMAL(10, 2) DEFAULT 0.00,
        vet_name VARCHAR(200),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (visit_id) REFERENCES veterinary_visits(id) ON DELETE SET NULL,
        INDEX idx_animal_tag (animal_tag),
        INDEX idx_treatment_date (treatment_date),
        INDEX idx_visit_id (visit_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(veterinary_treatments_table)
        conn.commit()
        print("✓ veterinary_treatments table created successfully")
    except Exception as e:
        print(f"✗ Error creating veterinary_treatments table: {str(e)}")
        conn.rollback()
    
    # 3. Medical History Table (Enhanced)
    medical_history_table = """
    CREATE TABLE IF NOT EXISTS medical_history_detailed (
        id INT AUTO_INCREMENT PRIMARY KEY,
        animal_tag VARCHAR(100) NOT NULL,
        animal_name VARCHAR(200),
        date DATE NOT NULL,
        record_type ENUM('Vaccination', 'Treatment', 'Surgery', 'Checkup', 'Disease', 'Injury', 'Other') NOT NULL,
        disease_name VARCHAR(300),
        diagnosis TEXT,
        treatment TEXT,
        medicines_used TEXT,
        vet_name VARCHAR(200),
        cost DECIMAL(10, 2) DEFAULT 0.00,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_animal_tag (animal_tag),
        INDEX idx_date (date),
        INDEX idx_record_type (record_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(medical_history_table)
        conn.commit()
        print("✓ medical_history_detailed table created successfully")
    except Exception as e:
        print(f"✗ Error creating medical_history_detailed table: {str(e)}")
        conn.rollback()
    
    # 4. Vaccination Schedule Table
    vaccination_schedule_table = """
    CREATE TABLE IF NOT EXISTS vaccination_schedule (
        id INT AUTO_INCREMENT PRIMARY KEY,
        animal_tag VARCHAR(100) NOT NULL,
        animal_name VARCHAR(200),
        vaccine_name VARCHAR(300) NOT NULL,
        scheduled_date DATE NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        completion_date DATE NULL,
        vet_name VARCHAR(200),
        cost DECIMAL(10, 2) DEFAULT 0.00,
        notes TEXT,
        reminder_sent BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_animal_tag (animal_tag),
        INDEX idx_scheduled_date (scheduled_date),
        INDEX idx_completed (completed)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(vaccination_schedule_table)
        conn.commit()
        print("✓ vaccination_schedule table created successfully")
    except Exception as e:
        print(f"✗ Error creating vaccination_schedule table: {str(e)}")
        conn.rollback()
    
    # 5. Veterinary Reports/Documents Table
    veterinary_reports_table = """
    CREATE TABLE IF NOT EXISTS veterinary_reports (
        id INT AUTO_INCREMENT PRIMARY KEY,
        visit_id INT NULL,
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(veterinary_reports_table)
        conn.commit()
        print("✓ veterinary_reports table created successfully")
    except Exception as e:
        print(f"✗ Error creating veterinary_reports table: {str(e)}")
        conn.rollback()
    
    # 6. Common Diseases Reference Table
    diseases_table = """
    CREATE TABLE IF NOT EXISTS common_diseases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        disease_name VARCHAR(300) NOT NULL,
        category VARCHAR(100),
        symptoms TEXT,
        common_treatment TEXT,
        prevention TEXT,
        severity ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_disease_name (disease_name),
        INDEX idx_category (category)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(diseases_table)
        conn.commit()
        print("✓ common_diseases table created successfully")
    except Exception as e:
        print(f"✗ Error creating common_diseases table: {str(e)}")
        conn.rollback()
    
    cursor.close()
    conn.close()
    
    print("\n✓ All veterinary tables created successfully!")
    return True


def insert_sample_diseases():
    """Insert sample common diseases for reference"""
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "khamarbari")
    )
    cursor = conn.cursor()
    
    sample_diseases = [
        ("FMD (Foot and Mouth Disease)", "Viral", "Fever, blisters in mouth and on feet, excessive salivation", 
         "Vaccination, supportive care, antibiotics for secondary infections", "Regular FMD vaccination", "High"),
        ("Mastitis", "Bacterial", "Swollen udder, abnormal milk, fever", 
         "Antibiotics (Penicillin), anti-inflammatory drugs", "Proper milking hygiene, regular checks", "Medium"),
        ("Blackleg", "Bacterial", "Sudden death, lameness, fever, swelling", 
         "Antibiotics (if caught early), vaccination", "Annual Blackleg vaccination", "Critical"),
        ("Bloat", "Digestive", "Distended abdomen, difficulty breathing, distress", 
         "Immediate veterinary care, trocar or stomach tube", "Gradual diet changes, proper feeding", "High"),
        ("Pneumonia", "Respiratory", "Coughing, nasal discharge, fever, difficulty breathing", 
         "Antibiotics, anti-inflammatory drugs, supportive care", "Proper ventilation, vaccination", "Medium"),
        ("Diarrhea/Scours", "Digestive", "Watery feces, dehydration, weakness", 
         "Oral rehydration, antibiotics if bacterial", "Clean environment, proper nutrition", "Medium"),
        ("Tick-borne Diseases", "Parasitic", "Fever, anemia, weakness, loss of appetite", 
         "Anti-tick medications, supportive care", "Regular tick control, dipping", "Medium"),
        ("Tuberculosis", "Bacterial", "Chronic cough, weight loss, weakness", 
         "Culling of infected animals, testing program", "Regular TB testing, biosecurity", "High"),
        ("Ringworm", "Fungal", "Circular hair loss, crusty skin patches", 
         "Antifungal treatments, topical medications", "Isolation of infected animals, disinfection", "Low"),
        ("Pink Eye", "Bacterial", "Redness, discharge, cloudiness of eye", 
         "Antibiotic eye ointment, isolation", "Fly control, reduce dust", "Low")
    ]
    
    try:
        for disease in sample_diseases:
            cursor.execute("""
                INSERT IGNORE INTO common_diseases 
                (disease_name, category, symptoms, common_treatment, prevention, severity)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, disease)
        
        conn.commit()
        print("✓ Sample diseases inserted successfully")
    except Exception as e:
        print(f"✗ Error inserting sample diseases: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Veterinary Database Setup")
    print("=" * 60)
    
    create_veterinary_tables()
    insert_sample_diseases()
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
