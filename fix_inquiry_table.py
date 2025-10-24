#!/usr/bin/env python3
import sqlite3

def fix_inquiry_table():
    conn = sqlite3.connect('jshoes.db')
    cursor = conn.cursor()
    
    # Get current table info
    cursor.execute("PRAGMA table_info(inquiry)")
    columns = cursor.fetchall()
    print("Current columns:", [col[1] for col in columns])
    
    # Check if is_read exists
    has_is_read = any(col[1] == 'is_read' for col in columns)
    
    if not has_is_read:
        print("Adding is_read column...")
        cursor.execute("ALTER TABLE inquiry ADD COLUMN is_read BOOLEAN DEFAULT 0")
        conn.commit()
        print("Column added successfully")
    else:
        print("is_read column already exists")
    
    # Verify the fix
    cursor.execute("PRAGMA table_info(inquiry)")
    columns = cursor.fetchall()
    print("Updated columns:", [col[1] for col in columns])
    
    conn.close()

if __name__ == '__main__':
    fix_inquiry_table()