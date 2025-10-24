#!/usr/bin/env python3
"""
Database initialization script for JShoes
Run this to set up the database schema and create initial admin user
"""

from app import create_app
from models import db
from models.user import User
from models.admin import AdminSettings

def init_database():
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("Creating admin user...")
            admin_user = User(username='admin', email='admin@jshoes.com', is_admin=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
        
        # Create default admin settings
        default_settings = [
            ('site_name', 'JShoes Store', 'Website name'),
            ('site_email', 'admin@jshoes.com', 'Contact email'),
            ('currency', 'USD', 'Default currency'),
            ('tax_rate', '0.08', 'Tax rate (decimal)'),
        ]
        
        for key, value, desc in default_settings:
            setting = AdminSettings.query.filter_by(key=key).first()
            if not setting:
                setting = AdminSettings(key=key, value=value, description=desc)
                db.session.add(setting)
        
        db.session.commit()
        print("Database initialized successfully!")
        print("Admin credentials: username='admin', password='admin123'")

if __name__ == '__main__':
    init_database()