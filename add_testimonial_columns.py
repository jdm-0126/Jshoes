#!/usr/bin/env python3
import sqlite3

def add_testimonial_columns():
    conn = sqlite3.connect('jshoes.db')
    cursor = conn.cursor()
    
    # Get current table info
    cursor.execute("PRAGMA table_info(contact_settings)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Current columns:", columns)
    
    # Add testimonial columns if they don't exist
    testimonial_columns = [
        ('testimonial1_text', 'TEXT', 'Amazing quality shoes! Fast delivery and excellent customer service. Highly recommended!'),
        ('testimonial1_author', 'VARCHAR(100)', 'Maria Santos'),
        ('testimonial2_text', 'TEXT', 'Perfect fit and comfortable. Great selection of styles. Will definitely order again!'),
        ('testimonial2_author', 'VARCHAR(100)', 'John Cruz'),
        ('testimonial3_text', 'TEXT', 'Best online shoe store! Affordable prices and trendy designs. Love shopping here!'),
        ('testimonial3_author', 'VARCHAR(100)', 'Ana Reyes')
    ]
    
    for col_name, col_type, default_value in testimonial_columns:
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE contact_settings ADD COLUMN {col_name} {col_type} DEFAULT '{default_value}'")
            print(f"Added {col_name} column")
    
    conn.commit()
    conn.close()
    print("Database updated successfully!")

if __name__ == '__main__':
    add_testimonial_columns()