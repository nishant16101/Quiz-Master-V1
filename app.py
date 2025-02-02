from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '9881560237'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'user_login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)

# Flask-Login Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Admin Routes
@app.route('/admin/login.html', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, is_admin=True).first()  # Ensure user is admin
        if user and user.check_password(password):
            login_user(user)
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
        flash('Invalid username or password', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user/dashboard'))
    return render_template('admin/dashboard.html')

@app.route('/admin/subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
    subjects = Subject.query.all()
    return render_template('admin/add-subject.html', subjects=subjects)

@app.route('/admin/subject/delete/<int:subject_id>')
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('manage_subjects'))

@app.route('/admin/chapters', methods=['GET', 'POST'])
@login_required
def manage_chapters():
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        name = request.form.get('name')
        description = request.form.get('description')
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
    chapters = Chapter.query.all()
    subjects = Subject.query.all()
    return render_template('admin/add-chapter.html', chapters=chapters, subjects=subjects)

@app.route('/admin/chapter/delete/<int:chapter_id>')
@login_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('manage_chapters'))

@app.route('/admin/quizzes', methods=['GET', 'POST'])
@login_required
def manage_quizzes():
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        title = request.form.get('title')
        duration = request.form.get('duration')
        quiz = Quiz(title=title, duration=duration, chapter_id=chapter_id)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
    quizzes = Quiz.query.all()
    chapters = Chapter.query.all()
    return render_template('admin/add-quiz.html', quizzes=quizzes, chapters=chapters)

@app.route('/admin/quiz/delete/<int:quiz_id>')
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('manage_quizzes'))

@app.route('/quiz/<int:quiz_id>/questions', methods=['GET', 'POST'])
def view_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/question.html', quiz_name=quiz.title, quiz_id=quiz.id, questions=questions)




@app.route('/admin/questions/<int:quiz_id>/add', methods=['POST'])
@login_required
def add_question(quiz_id):
    content = request.form.get('question_text')  # Ensure correct field names from the form
    option_a = request.form.get('option_1')
    option_b = request.form.get('option_2')
    option_c = request.form.get('option_3')
    option_d = request.form.get('option_4')
    correct_answer = request.form.get('correct_option')
    
    if not all([content, option_a, option_b, option_c, option_d, correct_answer]):
        flash('All fields are required!', 'danger')
        return redirect(url_for('view_questions', quiz_id=quiz_id))
    
    new_question = Question(
        content=content, 
        option_a=option_a, 
        option_b=option_b, 
        option_c=option_c, 
        option_d=option_d, 
        correct_answer=correct_answer, 
        quiz_id=quiz_id
    )
    
    db.session.add(new_question)
    db.session.commit()
    flash('Question added successfully!', 'success')
    return redirect(url_for('view_questions', quiz_id=quiz_id))


@app.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id  
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('view_questions', quiz_id=quiz_id))


# User Routes
@app.route('/user/login.html', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('user/login.html')

@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('user_register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user_login'))
    return render_template('user/register.html')
@app.route('/user/dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    available_quizzes = Quiz.query.all()
    attempted_quizzes = QuizAttempt.query.filter_by(user_id=current_user.id).all()
    return render_template('user/dashboard.html', 
                           available_quizzes=available_quizzes, 
                           attempted_quizzes=attempted_quizzes)

@app.route('/user/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('user/quiz.html', quiz=quiz, questions=questions)


@app.route('/user/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    score = 0
    for question in questions:
        answer = request.form.get(f'q{question.id}')
        if answer == question.correct_answer:
            score += 1
    
    attempt = QuizAttempt(user_id=current_user.id, 
                         quiz_id=quiz_id, 
                         score=score)
    db.session.add(attempt)
    db.session.commit()
    flash('Quiz submitted successfully!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password and password == confirm_password:
            current_user.set_password(password)
        current_user.username = username
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile'))
    return render_template('user/profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')  # Set password to 'admin123'
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)