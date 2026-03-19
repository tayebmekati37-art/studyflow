import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Word, QuizResult, Generation
from forms import RegistrationForm, LoginForm, WordForm
from config import Config
from sqlalchemy import func
import random
import json

# AI imports
from ai_service import generate_summary, generate_flashcards, generate_quiz
import PyPDF2

# Initialize extensions
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'

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
        levels = ['N5','N4','N3','N2','N1']
        data = {level: 0 for level in levels}
        for level, count in counts:
            data[level] = count
        recent_words = Word.query.filter_by(user_id=current_user.id).order_by(Word.created_at.desc()).limit(5).all()
        return render_template('index.html', data=data, recent_words=recent_words)

    @app.route('/words')
    @login_required
    def words():
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
        form = WordForm(obj=word)
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
        words = Word.query.filter_by(user_id=current_user.id).all()
        if len(words) < 4:
            flash('You need at least 4 words to take a quiz.', 'warning')
            return redirect(url_for('words'))

        if request.method == 'POST':
            score = 0
            total = int(request.form.get('total', 0))
            for i in range(total):
                word_id = request.form.get(f'q_{i}_id')
                answer = request.form.get(f'q_{i}_answer')
                word = Word.query.get(word_id)
                if word and word.meaning == answer:
                    score += 1
            result = QuizResult(user_id=current_user.id, score=score, total_questions=total)
            db.session.add(result)
            db.session.commit()
            return render_template('quiz_result.html', score=score, total=total)

        sample_size = min(10, len(words))
        quiz_words = random.sample(words, sample_size)
        questions = []
        for word in quiz_words:
            other_meanings = [w.meaning for w in words if w.id != word.id]
            if len(other_meanings) < 3:
                dummy = ['apple', 'cat', 'book', 'run', 'eat']
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

    # ---------- NEW AI TOOL ROUTES ----------
    @app.route('/study_tools')
    @login_required
    def study_tools():
        """Main AI tools page."""
        return render_template('study_tools.html')

    @app.route('/process_text', methods=['POST'])
    @login_required
    def process_text():
        """Handle text/PDF input and generate AI output."""
        tool_type = request.form.get('tool_type')  # summary, flashcard, quiz
        text_input = request.form.get('text', '')
        source_lang = request.form.get('source_lang', 'auto')
        target_lang = request.form.get('target_lang', 'en')
        
        # Handle file upload if present
        if 'pdf_file' in request.files:
            pdf_file = request.files['pdf_file']
            if pdf_file.filename != '':
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text_input = ''
                for page in pdf_reader.pages:
                    text_input += page.extract_text()
        
        if not text_input:
            flash('Please provide text or upload a PDF.', 'danger')
            return redirect(url_for('study_tools'))
        
        # Generate based on tool type
        try:
            if tool_type == 'summary':
                output = generate_summary(text_input, source_lang, target_lang)
                output_json = json.dumps({"summary": output})
            elif tool_type == 'flashcard':
                flashcards = generate_flashcards(text_input, source_lang)
                output_json = json.dumps(flashcards)
            elif tool_type == 'quiz':
                quiz = generate_quiz(text_input, source_lang)
                output_json = json.dumps(quiz)
            else:
                flash('Invalid tool type.', 'danger')
                return redirect(url_for('study_tools'))
            
            # Save generation to database
            generation = Generation(
                user_id=current_user.id,
                tool_type=tool_type,
                input_text=text_input[:500],  # Truncate for storage
                output_content=output_json,
                source_language=source_lang,
                target_language=target_lang
            )
            db.session.add(generation)
            db.session.commit()
            
            # Pass result to result page
            return render_template('tool_result.html', 
                                   tool_type=tool_type,
                                   output=output_json,
                                   generation_id=generation.id)
        
        except Exception as e:
            flash(f'Error generating content: {str(e)}', 'danger')
            return redirect(url_for('study_tools'))

    @app.route('/history')
    @login_required
    def history():
        """Show user's generation history."""
        generations = Generation.query.filter_by(user_id=current_user.id)\
                                      .order_by(Generation.created_at.desc())\
                                      .all()
        return render_template('history.html', generations=generations)

    @app.route('/generation/<int:gen_id>')
    @login_required
    def view_generation(gen_id):
        """View a specific generation."""
        gen = Generation.query.get_or_404(gen_id)
        if gen.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('history'))
        return render_template('tool_result.html', 
                               tool_type=gen.tool_type,
                               output=gen.output_content,
                               generation=gen)

    # API endpoint for progress chart data
    @app.route('/api/progress')
    @login_required
    def api_progress():
        counts = db.session.query(Word.jlpt_level, func.count(Word.id)).filter_by(user_id=current_user.id).group_by(Word.jlpt_level).all()
        data = {level: 0 for level in ['N5','N4','N3','N2','N1']}
        for level, count in counts:
            data[level] = count
        return jsonify(data)

    return app

# This block is only used when running directly (not imported)
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)