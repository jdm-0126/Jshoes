from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class InquiryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[('sneakers', 'Sneakers'), ('boots', 'Boots'), ('running', 'Running'), ('sandals', 'Sandals')])
    image_url = StringField('Image URL')