import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY_P', 'not-set')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')