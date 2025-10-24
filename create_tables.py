#!/usr/bin/env python3
"""
Force create tables in MySQL database
"""

import os
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from models import db

def create_tables():
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating all tables...")
            db.create_all()
            print("SUCCESS: Tables created successfully!")
            
            # Verify tables were created
            result = db.engine.execute("SHOW TABLES")
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"SUCCESS: Created {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("ERROR: No tables found after creation")
                
        except Exception as e:
            print(f"ERROR: Creating tables failed: {e}")

if __name__ == '__main__':
    create_tables()