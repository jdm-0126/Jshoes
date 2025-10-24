from . import db

class ContactSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), default='+63 123 456 7890')
    email = db.Column(db.String(120), default='info@jshoes.com')
    address = db.Column(db.Text, default='123 Shoe Street, Manila, Philippines')
    business_hours = db.Column(db.String(100), default='Mon-Sat: 9AM-6PM, Sun: 10AM-4PM')
    facebook_url = db.Column(db.String(200), default='https://www.facebook.com/profile.php?id=61564021213335')
    instagram_url = db.Column(db.String(200), default='https://www.instagram.com/jshoes_ph/')
    
    @property
    def testimonial1_text(self):
        return 'Amazing quality shoes! Fast delivery and excellent customer service. Highly recommended!'
    
    @property
    def testimonial1_author(self):
        return 'Maria Santos'
    
    @property
    def testimonial2_text(self):
        return 'Perfect fit and comfortable. Great selection of styles. Will definitely order again!'
    
    @property
    def testimonial2_author(self):
        return 'John Cruz'
    
    @property
    def testimonial3_text(self):
        return 'Best online shoe store! Affordable prices and trendy designs. Love shopping here!'
    
    @property
    def testimonial3_author(self):
        return 'Ana Reyes'
    
    @classmethod
    def get_settings(cls):
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings