from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    challenges = db.relationship('Challenge', backref='creator', lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True)
    statuses = db.relationship('UserChallengeStatus', backref='user', lazy=True)
    completed_challenges = db.relationship('CompletedChallenge', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    challenge_type = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    goals = db.relationship('Goal', backref='challenge', lazy=True, cascade="all, delete-orphan")
    badges = db.relationship('ChallengeBadge', backref='challenge', lazy=True, cascade="all, delete-orphan")
    chat_messages = db.relationship('ChatMessage', backref='challenge', lazy=True, cascade="all, delete-orphan")
    statuses = db.relationship('UserChallengeStatus', backref='challenge', lazy=True, cascade="all, delete-orphan")
    completions = db.relationship('CompletedChallenge', backref='challenge', lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship('Favorite', backref='challenge', lazy=True, cascade="all, delete-orphan")

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    goal_text = db.Column(db.Text, nullable=False)

class ChallengeBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    badge = db.Column(db.String(80), nullable=False)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=func.now())

class UserChallengeStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    is_complete = db.Column(db.Boolean, default=False)

class CompletedChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    fully_completed = db.Column(db.Boolean, default=False)  # New flag

class Favorite(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), primary_key=True)
