from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db, login_manager
from models.user import User
from utils.email_service import init_mail
from utils.error_logger import setup_error_logging, log_error

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup error logging
    setup_error_logging(app)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail = init_mail(app)
    app.mail = mail
    
    # Add timedelta to template context
    from datetime import timedelta
    @app.context_processor
    def inject_timedelta():
        return dict(timedelta=timedelta)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.main_routes import main
    from routes.auth_routes import auth
    from routes.cart_routes import cart
    from routes.admin_routes import admin
    from routes.payment_routes import payment
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(cart)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(payment)
    
    # Import delivery models to ensure they're registered
    from models.delivery import Delivery, DeliveryItem
    from models.contact_settings import ContactSettings
    from models.review import Review
    from models.inventory_alert import InventoryAlert
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            
            # Create admin user if not exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin', email='admin@jshoes.com', is_admin=True)
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
        except Exception as e:
            log_error("Database initialization failed", e)
            # Continue without admin user creation if there's an error
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)