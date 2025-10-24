#!/usr/bin/env python3
"""
Add is_read column to inquiry table
"""
import sqlite3
import os

def add_inquiry_read_column():
    db_path = 'jshoes.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(inquiry)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_read' not in columns:
            # Add the is_read column
            cursor.execute("ALTER TABLE inquiry ADD COLUMN is_read BOOLEAN DEFAULT 0")
            print("Added is_read column to inquiry table")
        else:
            print("is_read column already exists")
        
        conn.commit()
        conn.close()
        print("Database updated successfully!")
        
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == '__main__':
    add_inquiry_read_column()