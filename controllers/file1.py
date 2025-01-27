from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from models import db,Subject,Chapter,Quiz,Question

admin_bp = Blueprint('admin',__name__)

@admin_bp.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            #login admin
            return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/subjects',methods=['GET','POST'])
@login_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        subject = Subject(name = name,description=description)
        db.session.add(subject)
        db.session.commit()
    subjects = Subject.query.all()
    return render_template('admin/subjects.html',subjects=subjects)

@admin_bp.route('/subject/delete/<int:subject_id>')
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully')
    except:
        flash('Error deleting subject. Please delete associated chapters first.')
    return redirect(url_for('admin.manage_subjects'))


@admin_bp.route('/quizzes',methods = ['GET','POST'])
@login_required
def manange_chapters():
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        name = request.form.get('name')
        description = request.form.get('description')
        chapter = Chapter(name=name,description=description,subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
    chapters = Chapter.query.all()
    subjects =Subject.query.all()
    return render_template('admin/chapters.html',chapters=chapters,subjects=subjects)


@admin_bp.route('/chapter/delete/<int:chapter_id>')
@login_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    try:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully')
    except:
        flash('Error deleting chapter. Please delete associated quizzes first.')
    return redirect(url_for('admin.manage_chapters'))

@admin_bp.route('/quizzes',methods=['GET','POST'])
@login_required
def manage_quizzes():
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        title = request.form.get('title')
        duration = request.form.get('duration')
        quiz = Quiz(title=title,duration=duration,chapter_id=chapter_id)
        db.session.add(quiz)
        db.session.commit()
    quizzes = Quiz.query.all()
    chapters = Chapter.query.all()
    return render_template('admin/quizzes.html',quizzes=quizzes,chapters=chapters)

@admin_bp.route('/quiz/delete/<int:quiz_id>')
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    try:
        # First delete associated questions
        Question.query.filter_by(quiz_id=quiz_id).delete()
        # Then delete the quiz
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully')
    except:
        flash('Error deleting quiz')
    return redirect(url_for('admin.manage_quizzes'))        

