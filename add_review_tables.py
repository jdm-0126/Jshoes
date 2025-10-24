import sqlite3
import os

# Try both database locations
db_paths = ['jshoes.db', 'instance/jshoes.db']

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Updating database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create review table
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (product_id) REFERENCES product (id)
                )
            ''')
            print("Review table created/verified")
        except Exception as e:
            print(f"Error creating review table: {e}")
        
        # Create inventory_alert table
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_alert (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    alert_threshold INTEGER DEFAULT 5,
                    is_active BOOLEAN DEFAULT 1,
                    last_alert_sent DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES product (id)
                )
            ''')
            print("InventoryAlert table created/verified")
        except Exception as e:
            print(f"Error creating inventory_alert table: {e}")
        
        # Create contact_settings table
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone VARCHAR(20) DEFAULT '+63 123 456 7890',
                    email VARCHAR(120) DEFAULT 'info@jshoes.com',
                    address TEXT DEFAULT '123 Shoe Street, Manila, Philippines',
                    business_hours VARCHAR(100) DEFAULT 'Mon-Sat: 9AM-6PM, Sun: 10AM-4PM',
                    facebook_url VARCHAR(200) DEFAULT 'https://www.facebook.com/profile.php?id=61564021213335',
                    instagram_url VARCHAR(200) DEFAULT 'https://www.instagram.com/jshoes_ph/'
                )
            ''')
            print("ContactSettings table created/verified")
        except Exception as e:
            print(f"Error creating contact_settings table: {e}")
        
        conn.commit()
        conn.close()
        print(f"Database {db_path} updated successfully")

print("All tables created/updated successfully!")