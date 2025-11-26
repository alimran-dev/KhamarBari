#!/usr/bin/env python3
"""Script to check and manage users in the database"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config.db import get_connection

def list_users():
    """List all users in the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT email, owner_name, farm_name, phone_number FROM users")
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not users:
            print("No users found in the database.")
            return []
        
        print("\n=== Users in Database ===")
        for user in users:
            print(f"\nEmail: {user[0]}")
            print(f"Owner Name: {user[1]}")
            print(f"Farm Name: {user[2]}")
            print(f"Phone: {user[3]}")
            print("-" * 40)
        
        return users
    
    except Exception as e:
        print(f"Error: {e}")
        return []

def add_test_user():
    """Add a test user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        email = "i@gmail.com"
        
        # Check if user exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"User {email} already exists!")
            cursor.close()
            conn.close()
            return
        
        # Insert test user
        cursor.execute(
            """INSERT INTO users (email, password, owner_name, farm_name, phone_number) 
               VALUES (%s, %s, %s, %s, %s)""",
            (email, "123456", "Al Imran", "Imrans Farm", "01711111111")
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Test user {email} created successfully!")
        print("Password: 123456")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        add_test_user()
    
    list_users()
