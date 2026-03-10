from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class WordForm(FlaskForm):
    japanese_word = StringField('Japanese Word', validators=[DataRequired()])
    reading = StringField('Reading (hiragana)', validators=[DataRequired()])
    meaning = StringField('Meaning', validators=[DataRequired()])
    jlpt_level = SelectField('JLPT Level', choices=[('N5','N5'), ('N4','N4'), ('N3','N3'), ('N2','N2'), ('N1','N1')], validators=[DataRequired()])
    submit = SubmitField('Save Word')