from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from datetime import datetime
import numpy as np
from config import Config
import os


app = Flask(__name__)
app.config.from_object(Config)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/stephenkohlmann1/Flask_Projects/Blog_PostgreSQL/blog.db'
#app.config['SECRET_KEY'] = 'your_secret_key'

#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://flask_blog_m015_user:3LoDM02ITkdfm5MFQxiRH4p44UEGsQ5F@dpg-cjd467bbq8nc738a26t0-a.frankfurt-postgres.render.com/flask_blog_m015"
#postgres://flask_blog_m015_user:3LoDM02ITkdfm5MFQxiRH4p44UEGsQ5F@dpg-cjd467bbq8nc738a26t0-a.frankfurt-postgres.render.com/flask_blog_m015

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

db = SQLAlchemy(app)
       
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    posts = BlogPost.query.all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        # Perform logout operation
        logout_user()
        return redirect(url_for('index'))
    else:
        return render_template('logout.html')

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = current_user.username
        post = BlogPost(title=title, content=content, author=author)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    return render_template('edit.html', post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/stats')
def stats():
    posts = BlogPost.query.all()
    title_lengths = [len(post.title) for post in posts]

    average_length = np.mean(title_lengths)
    max_length = np.max(title_lengths)
    min_length = np.min(title_lengths)
    total_length = np.sum(title_lengths)
    median_length = np.median(title_lengths)

    return render_template('stats.html', average_length=average_length, max_length=max_length,
                           min_length=min_length, total_length=total_length, median_length=median_length)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

  
