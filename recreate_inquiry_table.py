#!/usr/bin/env python3
import sqlite3

def recreate_inquiry_table():
    conn = sqlite3.connect('jshoes.db')
    cursor = conn.cursor()
    
    # Backup existing data
    cursor.execute("SELECT * FROM inquiry")
    existing_data = cursor.fetchall()
    print(f"Found {len(existing_data)} existing inquiries")
    
    # Drop and recreate table
    cursor.execute("DROP TABLE IF EXISTS inquiry")
    cursor.execute('''
        CREATE TABLE inquiry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL,
            subject VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'new',
            is_read BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Restore data
    for row in existing_data:
        cursor.execute('''
            INSERT INTO inquiry (id, name, email, subject, message, status, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row[0], row[1], row[2], row[3], row[4], row[5], 0, row[6]))
    
    conn.commit()
    conn.close()
    print("Inquiry table recreated successfully with is_read column")

if __name__ == '__main__':
    recreate_inquiry_table()