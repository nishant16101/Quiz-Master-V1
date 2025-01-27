from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primart_key = True)
    username = db.Column(db.String(88),unique =True,nullable =False)
    password = db.Column(db.String(120),nullable = False)
    is_admin = db.Column(db.Boolean,default = False)
    quiz_attempt = db.relationship('QuizAttempt',backref = 'user',lazy =True)

class Subject(db.Model):
    id = db.Column(db.Integer,primary_key =True)
    name = db.Column(db.String(100),nullable =False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter',backref = 'subject',lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer,primary_key =True)
    name = db.Column(db.String(100),nullable = False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer,db.ForeignKey('subject.id'),nullable =False)
    quizzes = db.relationship('Quiz',backref = 'chapter',lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(100),nullable=False)
    duration = db.Column(db.Integer,nullable = False)
    chapter_id = db.Column(db.Integer,db.ForeignKey('chapter.id'),nullable = False)
    questions = db.relationship('Question',backref = 'quiz  ',lazy = True)
    attempts = db.relationship('QuizAttempt',backref ='quiz',lazy = True)

class Question(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text,nullable =False)
    option_a = db.Column(db.String(200),nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    user_id= db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    quiz_id = db.Column(db.Integer,db.ForeignKey('quiz.id'),nullable=False)
    score = db.Column(db.Integer,nullable=False)
    date_attempted = db.Column(db.DateTime,default = datetime.now)

