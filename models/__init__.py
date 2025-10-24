from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def init_app(app):
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

from . import product, order, user
from . import cart  # add this line