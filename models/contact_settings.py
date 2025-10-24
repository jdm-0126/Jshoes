from . import db

class ContactSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), default='+63 123 456 7890')
    email = db.Column(db.String(120), default='info@jshoes.com')
    address = db.Column(db.Text, default='123 Shoe Street, Manila, Philippines')
    business_hours = db.Column(db.String(100), default='Mon-Sat: 9AM-6PM, Sun: 10AM-4PM')
    facebook_url = db.Column(db.String(200), default='https://www.facebook.com/profile.php?id=61564021213335')
    instagram_url = db.Column(db.String(200), default='https://www.instagram.com/jshoes_ph/')
    
    @classmethod
    def get_settings(cls):
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings