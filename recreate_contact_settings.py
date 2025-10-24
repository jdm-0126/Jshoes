#!/usr/bin/env python3
import sqlite3

def recreate_contact_settings():
    conn = sqlite3.connect('jshoes.db')
    cursor = conn.cursor()
    
    # Backup existing data
    cursor.execute("SELECT * FROM contact_settings")
    existing_data = cursor.fetchall()
    print(f"Found {len(existing_data)} existing settings")
    
    # Drop and recreate table
    cursor.execute("DROP TABLE IF EXISTS contact_settings")
    cursor.execute('''
        CREATE TABLE contact_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone VARCHAR(20) DEFAULT '+63 123 456 7890',
            email VARCHAR(120) DEFAULT 'info@jshoes.com',
            address TEXT DEFAULT '123 Shoe Street, Manila, Philippines',
            business_hours VARCHAR(100) DEFAULT 'Mon-Sat: 9AM-6PM, Sun: 10AM-4PM',
            facebook_url VARCHAR(200) DEFAULT 'https://www.facebook.com/profile.php?id=61564021213335',
            instagram_url VARCHAR(200) DEFAULT 'https://www.instagram.com/jshoes_ph/',
            testimonial1_text TEXT DEFAULT 'Amazing quality shoes! Fast delivery and excellent customer service. Highly recommended!',
            testimonial1_author VARCHAR(100) DEFAULT 'Maria Santos',
            testimonial2_text TEXT DEFAULT 'Perfect fit and comfortable. Great selection of styles. Will definitely order again!',
            testimonial2_author VARCHAR(100) DEFAULT 'John Cruz',
            testimonial3_text TEXT DEFAULT 'Best online shoe store! Affordable prices and trendy designs. Love shopping here!',
            testimonial3_author VARCHAR(100) DEFAULT 'Ana Reyes'
        )
    ''')
    
    # Restore or create default data
    if existing_data:
        for row in existing_data:
            cursor.execute('''
                INSERT INTO contact_settings (id, phone, email, address, business_hours, facebook_url, instagram_url,
                testimonial1_text, testimonial1_author, testimonial2_text, testimonial2_author, testimonial3_text, testimonial3_author)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                  'Amazing quality shoes! Fast delivery and excellent customer service. Highly recommended!', 'Maria Santos',
                  'Perfect fit and comfortable. Great selection of styles. Will definitely order again!', 'John Cruz',
                  'Best online shoe store! Affordable prices and trendy designs. Love shopping here!', 'Ana Reyes'))
    else:
        cursor.execute('''
            INSERT INTO contact_settings (phone, email, address, business_hours, facebook_url, instagram_url,
            testimonial1_text, testimonial1_author, testimonial2_text, testimonial2_author, testimonial3_text, testimonial3_author)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('+63 123 456 7890', 'info@jshoes.com', '123 Shoe Street, Manila, Philippines', 'Mon-Sat: 9AM-6PM, Sun: 10AM-4PM',
              'https://www.facebook.com/profile.php?id=61564021213335', 'https://www.instagram.com/jshoes_ph/',
              'Amazing quality shoes! Fast delivery and excellent customer service. Highly recommended!', 'Maria Santos',
              'Perfect fit and comfortable. Great selection of styles. Will definitely order again!', 'John Cruz',
              'Best online shoe store! Affordable prices and trendy designs. Love shopping here!', 'Ana Reyes'))
    
    conn.commit()
    conn.close()
    print("Contact settings table recreated successfully with testimonials")

if __name__ == '__main__':
    recreate_contact_settings()