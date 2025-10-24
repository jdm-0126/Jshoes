import sqlite3
import os

# Try both database locations
db_paths = ['jshoes.db', 'instance/jshoes.db']

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Updating database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Add the is_viewer column to the user table
            cursor.execute('ALTER TABLE user ADD COLUMN is_viewer BOOLEAN DEFAULT 0')
            print("Successfully added is_viewer column to user table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column is_viewer already exists")
            else:
                print(f"Error: {e}")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        print(f"Database {db_path} updated successfully")
    else:
        print(f"Database not found: {db_path}")

print("Database update complete")