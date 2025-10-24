# JShoes - Flask E-commerce Store

A modern, responsive online shoe store built with Flask, featuring a clean design and data-driven analytics dashboard.

## Features

- **Customer Features:**
  - Browse shoe catalog with pagination
  - Product detail pages with images
  - Shopping cart functionality
  - User registration and authentication
  - Contact form for inquiries

- **Admin Features:**
  - Sales analytics dashboard
  - Product management (add, view, manage inventory)
  - Order tracking
  - Customer inquiry monitoring

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database:**
   ```bash
   # For development (SQLite)
   python init_db.py
   
   # For production (MySQL) - use migrations
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

3. **Run the Application:**
   ```bash
   python app.py
   ```

4. **Seed Sample Data (Optional):**
   ```bash
   python seed_data.py
   ```

4. **Access the Application:**
   - Website: http://localhost:5000
   - Admin Login: username=`admin`, password=`admin123`

## Project Structure

```
jshoes/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── wsgi.py               # Production WSGI entry point
├── models/               # Database models
├── routes/               # Flask blueprints
├── utils/                # Helper functions and forms
├── templates/            # HTML templates
└── static/               # CSS, JS, and images
```

## Database Models

- **User**: Customer accounts and admin users
- **Product**: Shoe inventory with categories
- **Order/OrderItem**: Purchase tracking
- **Inquiry**: Customer support messages
- **AdminLog**: Admin activity tracking
- **AdminSettings**: Site configuration settings

## Database Management

### Development (SQLite)
```bash
python init_db.py          # Initialize database
python manage.py           # Interactive setup
```

### Production (MySQL)
```bash
flask db init              # Initialize migrations
flask db migrate -m "msg"  # Create migration
flask db upgrade           # Apply migrations
flask db downgrade         # Rollback migrations
```

## Deployment

For production deployment (e.g., Hostinger):
1. Upload all files to your hosting directory
2. Set environment variables for production
3. The `wsgi.py` file serves as the entry point

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `SECRET_KEY`: Flask secret key for sessions
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: MySQL database credentials
- `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Email configuration
- `FLASK_ENV`: Set to 'production' for MySQL, 'development' for SQLite

## Admin Access

Default admin credentials:
- Username: `admin`
- Password: `admin123`

**Important:** Change these credentials in production!

## License

This project is open source and available under the MIT License.