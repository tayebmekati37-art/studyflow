from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    words = db.relationship('Word', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    quiz_results = db.relationship('QuizResult', backref='user', lazy='dynamic', cascade='all, delete-orphan')

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    japanese_word = db.Column(db.String(100), nullable=False)
    reading = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.String(200), nullable=False)
    jlpt_level = db.Column(db.Enum('N5','N4','N3','N2','N1'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)          # number correct
    total_questions = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)
class Generation(db.Model):
    __tablename__ = 'generations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tool_type = db.Column(db.Enum('summary', 'flashcard', 'quiz'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    output_content = db.Column(db.JSON, nullable=False)
    source_language = db.Column(db.String(10), default='auto')
    target_language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
