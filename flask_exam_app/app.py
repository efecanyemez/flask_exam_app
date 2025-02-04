from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import sys
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'exam.db')
app.config['SECRET_KEY'] = '2689451248971932a71417a6a00dabb6'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    highest_score = db.Column(db.Integer, default=0)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

def add_questions():
    questions = [
    { "question_text": "Python'da AI geliştirme için en yaygın kullanılan kütüphanelerden biri aşağıdakilerden hangisidir?",
      "option_a": "Django", "option_b": "TensorFlow", "option_c": "Flask",
      "option_d": "NumPy", "correct_answer": "B"},
    
    { "question_text": "Bir yapay sinir ağı modelini eğitmek için kullanılan temel algoritma aşağıdakilerden hangisidir?",
      "option_a": "Apriori", "option_b": "K-Means", "option_c": "Backpropagation",
      "option_d": "Decision Tree", "correct_answer": "C"},
    
    { "question_text": "Görüntü işleme için en yaygın kullanılan Python kütüphanelerinden biri aşağıdakilerden hangisidir?",
      "option_a": "OpenCV", "option_b": "NLTK", "option_c": "Scikit-learn",
      "option_d": "Pandas", "correct_answer": "A"},
    
    { "question_text": "Bir görüntüyü gri tonlamalı hale getirmek için kullanılan OpenCV fonksiyonu aşağıdakilerden hangisidir?",
      "option_a": "cv2.grayScale(img)", "option_b": "cv2.convertToGray(img)",
      "option_c": "cv2.toGray(img)", "option_d": "cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)",
      "correct_answer": "D"},
    
    { "question_text": "NLP (Doğal Dil İşleme) için kullanılan popüler bir kütüphane aşağıdakilerden hangisidir?",
      "option_a": "Matplotlib", "option_b": "Seaborn", "option_c": "Scipy",
      "option_d": "NLTK", "correct_answer": "D"},
    
    { "question_text": "Python’da metin verisini kelime vektörlerine dönüştürmek için yaygın olarak kullanılan yöntemlerden biri aşağıdakilerden hangisidir?",
      "option_a": "TF-IDF", "option_b": "Random Forest", "option_c": "PCA",
      "option_d": "Fourier Transform", "correct_answer": "A"},
    
    { "question_text": "Bir yapay zeka modelinin doğruluğunu değerlendirmek için kullanılan metriklerden biri aşağıdakilerden hangisidir?",
      "option_a": "Bitrate", "option_b": "Density", "option_c": "Throughput",
      "option_d": "Accuracy", "correct_answer": "D"},
    
    { "question_text": "Bir görüntüdeki kenarları tespit etmek için kullanılan en popüler algoritmalardan biri aşağıdakilerden hangisidir?",
      "option_a": "K-Means Clustering", "option_b": "Canny Edge Detection",
      "option_c": "Apriori Algorithm", "option_d": "Support Vector Machine",
      "correct_answer": "B"},
    
    { "question_text": "Bir metindeki duyguyu analiz etmek için kullanılan teknik aşağıdakilerden hangisidir?",
      "option_a": "Feature Extraction", "option_b": "Data Augmentation",
      "option_c": "Sentiment Analysis", "option_d": "Gradient Descent",
      "correct_answer": "C"},
    
    { "question_text": "Bir AI modelini Python uygulamalarına entegre etmek için kullanılan REST API çerçevesi aşağıdakilerden hangisidir?",
      "option_a": "FastAPI", "option_b": "Matplotlib", "option_c": "Pandas",
      "option_d": "Scikit-Learn", "correct_answer": "A"}
]


    for q in questions:
        existing = Question.query.filter_by(question_text=q["question_text"]).first()
        if not existing:
            new_question = Question(**q)
            db.session.add(new_question)
    db.session.commit()

@app.route('/')
def home():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    
    return render_template('index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 5 or len(password) < 5:
            error_message = "Kullanıcı adı ve şifre en az 5 karakter olmalıdır!"
            return render_template('register.html', error=error_message)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_message = "Bu kullanıcı adı zaten alınmış!"
            return render_template('register.html', error=error_message)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            error_message = "Geçersiz kullanıcı adı veya şifre!"
            return render_template('login.html', error=error_message)

        session['user_id'] = user.id
        return redirect(url_for('home'))

    return render_template('login.html', error=None)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_highest = user.highest_score  
    global_max_score = db.session.query(func.max(User.highest_score)).scalar()  

    if request.method == 'POST':
        q_ids_str = request.form.get("question_ids", "")
        ids_list = q_ids_str.split(",") if q_ids_str else []
        questions = Question.query.filter(Question.id.in_(ids_list)).all()
        
        score = 0
        total = len(questions)

        for q in questions:
            user_answer = request.form.get(str(q.id))  
            correct_answer = q.correct_answer  

            if user_answer and user_answer.strip().upper() == correct_answer.strip().upper():
                score += 1

        percent_score = (score / total) * 100 if total > 0 else 0

        if percent_score > user.highest_score:
            user.highest_score = percent_score
            db.session.commit()

        global_max_score = db.session.query(func.max(User.highest_score)).scalar()

        return render_template('result.html', score=percent_score, user_highest=user.highest_score, global_max=global_max_score)

    all_questions = Question.query.all()
    selected_questions = random.sample(all_questions, min(len(all_questions), 10))
    q_ids = ",".join(str(q.id) for q in selected_questions)

    return render_template(
        'quiz.html',
        questions=selected_questions,
        question_ids=q_ids,
        user_highest=user_highest,
        global_max=global_max_score
    )



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_questions()
    app.run(debug=False)