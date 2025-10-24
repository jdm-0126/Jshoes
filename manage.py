#!/usr/bin/env python3
"""
Database management commands for JShoes
"""

import click
from flask.cli import with_appcontext
from app import create_app
from models import db
from models.user import User
from models.product import Product
from models.admin import AdminSettings

app = create_app()

@click.command()
@with_appcontext
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo('Database initialized.')

@click.command()
@with_appcontext
def create_admin():
    """Create admin user."""
    admin = User.query.filter_by(username='admin').first()
    if admin:
        click.echo('Admin user already exists.')
        return
    
    admin = User(username='admin', email='admin@jshoes.com', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    click.echo('Admin user created: admin/admin123')

@click.command()
@with_appcontext
def reset_db():
    """Reset database (WARNING: Deletes all data)."""
    if click.confirm('This will delete all data. Continue?'):
        db.drop_all()
        db.create_all()
        click.echo('Database reset.')

if __name__ == '__main__':
    with app.app_context():
        if click.confirm('Initialize database?'):
            init_db()
        if click.confirm('Create admin user?'):
            create_admin()