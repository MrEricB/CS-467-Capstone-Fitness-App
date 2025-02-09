import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'secret_key_remove_for_production'  # Change for production & use env var
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'fitness_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    BADGES_FOLDER = os.path.join(basedir, 'static', 'badges')
