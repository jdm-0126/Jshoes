from app import create_app
from models import db

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Add new columns to user table
            conn.execute(db.text('ALTER TABLE user ADD COLUMN phone VARCHAR(20)'))
            conn.execute(db.text('ALTER TABLE user ADD COLUMN address TEXT'))
            conn.execute(db.text('ALTER TABLE user ADD COLUMN city VARCHAR(100)'))
            conn.execute(db.text('ALTER TABLE user ADD COLUMN postal_code VARCHAR(10)'))
            conn.commit()
        print("Successfully added user delivery fields")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("User delivery fields already exist")
        else:
            print(f"Error adding user fields: {e}")
    
    try:
        with db.engine.connect() as conn:
            # Add delivery_date column to order table
            conn.execute(db.text('ALTER TABLE "order" ADD COLUMN delivery_date DATE'))
            conn.commit()
        print("Successfully added delivery_date to orders table")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("Delivery date field already exists")
        else:
            print(f"Error adding delivery date field: {e}")