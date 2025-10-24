from app import create_app
from models import db

app = create_app()

with app.app_context():
    # Add the payment_source_id column to orders table
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE "order" ADD COLUMN payment_source_id VARCHAR(100)'))
            conn.commit()
        print("Successfully added payment_source_id column to orders table")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("Column payment_source_id already exists")
        else:
            print(f"Error adding column: {e}")