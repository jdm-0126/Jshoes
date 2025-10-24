import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_error_logging(app):
    """Setup error logging to file"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Create error log file handler
    file_handler = RotatingFileHandler('logs/errors.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('JShoes application startup')

def log_error(message, error=None):
    """Log error with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_msg = f"[{timestamp}] ERROR: {message}"
    if error:
        error_msg += f" - {str(error)}"
    
    # Write to file
    with open('logs/errors.log', 'a', encoding='utf-8') as f:
        f.write(error_msg + '\n')
    
    print(error_msg)  # Also print to console