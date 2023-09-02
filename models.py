from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    def __str__(self):
        return self.username


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return f'"{self.title}" by {self.author.username} ({self.created_at:%Y-%m-%d})'

    @staticmethod
    def get_title_lengths():
        # An example of how to use raw SQL in SQLAlchemy
        sql = text("SELECT length(title) FROM blog_post")
        return db.session.execute(sql).scalars().all()  # Returns just the integers

