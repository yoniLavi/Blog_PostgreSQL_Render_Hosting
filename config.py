import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY_P')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')