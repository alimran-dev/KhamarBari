#!/usr/bin/env python3
"""Add profile photo column to users table"""

import os
from dotenv import load_dotenv
from config.db import get_connection

load_dotenv()

def add_profile_photo_column():
    """Add photo_url column to users table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Adding photo_url column to users table...")
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN photo_url VARCHAR(255)")
            conn.commit()
            print("✓ Successfully added photo_url column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✓ Column photo_url already exists")
            else:
                raise
        
        cursor.close()
        conn.close()
        
        print("\nDatabase update completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_profile_photo_column()
