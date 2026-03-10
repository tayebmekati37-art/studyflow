import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Word, QuizResult
from forms import RegistrationForm, LoginForm, WordForm
from config import Config
from sqlalchemy import func
import random

# Initialize extensions
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    import pymysql
    pymysql.install_as_MySQLdb()
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'

    # Register blueprints if any, otherwise define routes here
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---------- Authentication Routes ----------
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Login unsuccessful. Check email and password.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    # ---------- Main Routes ----------
    @app.route('/')
    @login_required
    def index():
        # Dashboard: count words per JLPT level for current user
        counts = db.session.query(Word.jlpt_level, func.count(Word.id)).filter_by(user_id=current_user.id).group_by(Word.jlpt_level).all()
        # Convert to dict with zeros for missing levels
        levels = ['N5','N4','N3','N2','N1']
        data = {level: 0 for level in levels}
        for level, count in counts:
            data[level] = count
        # Recent words (last 5)
        recent_words = Word.query.filter_by(user_id=current_user.id).order_by(Word.created_at.desc()).limit(5).all()
        return render_template('index.html', data=data, recent_words=recent_words)

    @app.route('/words')
    @login_required
    def words():
        # Show all words, optionally filter by level via query param
        level = request.args.get('level')
        if level and level in ['N5','N4','N3','N2','N1']:
            words_list = Word.query.filter_by(user_id=current_user.id, jlpt_level=level).order_by(Word.japanese_word).all()
        else:
            words_list = Word.query.filter_by(user_id=current_user.id).order_by(Word.jlpt_level, Word.japanese_word).all()
        return render_template('words.html', words=words_list, current_level=level)

    @app.route('/add_word', methods=['GET', 'POST'])
    @login_required
    def add_word():
        form = WordForm()
        if form.validate_on_submit():
            word = Word(
                user_id=current_user.id,
                japanese_word=form.japanese_word.data,
                reading=form.reading.data,
                meaning=form.meaning.data,
                jlpt_level=form.jlpt_level.data
            )
            db.session.add(word)
            db.session.commit()
            flash('Word added successfully!', 'success')
            return redirect(url_for('words'))
        return render_template('add_word.html', form=form)

    @app.route('/edit_word/<int:word_id>', methods=['GET', 'POST'])
    @login_required
    def edit_word(word_id):
        word = Word.query.get_or_404(word_id)
        if word.user_id != current_user.id:
            flash('You cannot edit this word.', 'danger')
            return redirect(url_for('words'))
        form = WordForm(obj=word)  # pre-populate
        if form.validate_on_submit():
            word.japanese_word = form.japanese_word.data
            word.reading = form.reading.data
            word.meaning = form.meaning.data
            word.jlpt_level = form.jlpt_level.data
            db.session.commit()
            flash('Word updated!', 'success')
            return redirect(url_for('words'))
        return render_template('edit_word.html', form=form, word=word)

    @app.route('/delete_word/<int:word_id>', methods=['POST'])
    @login_required
    def delete_word(word_id):
        word = Word.query.get_or_404(word_id)
        if word.user_id != current_user.id:
            flash('You cannot delete this word.', 'danger')
            return redirect(url_for('words'))
        db.session.delete(word)
        db.session.commit()
        flash('Word deleted.', 'info')
        return redirect(url_for('words'))

    @app.route('/quiz', methods=['GET', 'POST'])
    @login_required
    def quiz():
        # Fetch all words of the user
        words = Word.query.filter_by(user_id=current_user.id).all()
        if len(words) < 4:
            flash('You need at least 4 words to take a quiz.', 'warning')
            return redirect(url_for('words'))

        if request.method == 'POST':
            # Process quiz answers
            score = 0
            total = int(request.form.get('total', 0))
            for i in range(total):
                word_id = request.form.get(f'q_{i}_id')
                answer = request.form.get(f'q_{i}_answer')
                word = Word.query.get(word_id)
                if word and word.meaning == answer:
                    score += 1
            # Save result
            result = QuizResult(user_id=current_user.id, score=score, total_questions=total)
            db.session.add(result)
            db.session.commit()
            return render_template('quiz_result.html', score=score, total=total)

        # GET: generate 10 random words (or less if fewer words)
        sample_size = min(10, len(words))
        quiz_words = random.sample(words, sample_size)
        # For each word, generate 3 random distractors (meanings from other words)
        questions = []
        for word in quiz_words:
            # Get 3 random distinct meanings from other words (excluding current word's meaning)
            other_meanings = [w.meaning for w in words if w.id != word.id]
            # If not enough other meanings, pad with placeholders
            if len(other_meanings) < 3:
                # Add some dummy meanings
                dummy = ['apple', 'cat', 'book', 'run', 'eat']  # simple fallback
                other_meanings.extend(dummy)
            options = random.sample(other_meanings, 3) + [word.meaning]
            random.shuffle(options)
            questions.append({
                'id': word.id,
                'japanese': word.japanese_word,
                'reading': word.reading,
                'options': options,
                'correct': word.meaning
            })
        return render_template('quiz.html', questions=questions)

    # API endpoint for progress chart data (optional, but used in dashboard via JavaScript)
    @app.route('/api/progress')
    @login_required
    def api_progress():
        counts = db.session.query(Word.jlpt_level, func.count(Word.id)).filter_by(user_id=current_user.id).group_by(Word.jlpt_level).all()
        data = {level: 0 for level in ['N5','N4','N3','N2','N1']}
        for level, count in counts:
            data[level] = count
        return jsonify(data)

    return app