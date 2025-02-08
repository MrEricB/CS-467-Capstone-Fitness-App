import os
from flask import Flask, render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import db, User, Challenge, Goal, ChallengeBadge, ChatMessage, UserChallengeStatus, CompletedChallenge, Favorite
from forms import RegistrationForm, LoginForm, ChallengeForm, ChatForm

app = Flask(__name__)
app.secret_key = 'sercert_key_change_for_production_and_put_in_envvar?'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fitness_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BADGES_FOLDER = os.path.join('static', 'badges')
app.config['BADGES_FOLDER'] = BADGES_FOLDER

db.init_app(app)

with app.app_context():
    db.create_all()
    # Create folders if they don't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['BADGES_FOLDER']):
        os.makedirs(app.config['BADGES_FOLDER'])

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(challenge_bp, url_prefix='/challenges')


if __name__ == '__main__':
    app.run(debug=True)
