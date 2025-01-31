from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Ensure this points to the correct DB file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    challenges_created = db.relationship('Challenge', backref='creator', lazy='dynamic')
    challenge_participations = db.relationship('ChallengeParticipation', backref='user', lazy='dynamic')
    badges = db.relationship('Badge', secondary='user_badges', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255))
    tags = db.relationship('Tag', secondary='challenge_tags', backref='challenges')
    goals = db.relationship('ChallengeGoal', backref='challenge', lazy='dynamic')
    participations = db.relationship('ChallengeParticipation', backref='challenge', lazy='dynamic')
    badges = db.relationship('Badge', secondary='challenge_badges', backref='challenges')

class ChallengeGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)

class ChallengeParticipation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    joined_date = db.Column(db.DateTime, default=func.now())
    is_completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime)

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_path = db.Column(db.String(255))

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())
    user = db.relationship('User', backref='chats')
    challenge = db.relationship('Challenge', backref='chats')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# Association Tables
user_badges = db.Table('user_badges',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'), primary_key=True)
)

challenge_badges = db.Table('challenge_badges',
    db.Column('challenge_id', db.Integer, db.ForeignKey('challenge.id'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'), primary_key=True)
)

challenge_tags = db.Table('challenge_tags',
    db.Column('challenge_id', db.Integer, db.ForeignKey('challenge.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


#################
## queries
#################

# Ensure you're running within an application context
with app.app_context():
    # Get all users
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

    # Get specific user by username
    user = User.query.filter_by(username="user2").first()
    if user:
        print(f"Found User: {user.username} - Email: {user.email}")

    # Update user’s email
    user = User.query.filter_by(username="user1").first()
    if user:
        user.email = "newemail@example.com"
        db.session.commit()
        print(f"Updated email: {user.email}")

    # Get all users again
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

    # Get all challenges created by a specific user
    user = User.query.filter_by(username="user1").first()
    if user:
        challenges = user.challenges_created.all()
        for challenge in challenges:
            print(f"Challenge: {challenge.title} - Created by {user.username}")

    # Get all challenges a user has participated in
    user = User.query.filter_by(username="user2").first()
    if user:
        participations = user.challenge_participations.all()
        for participation in participations:
            print(f"Participated in Challenge: {participation.challenge.title} - Completed: {participation.is_completed}")

    # # Get all challenges that have a specific tag
    # tag = Tag.query.filter_by(name="Fitness").first()
    # if tag:
    #     challenges = tag.challenges
    #     for challenge in challenges:
    #         print(f"Challenge: {challenge.title} - Tagged with: {tag.name}")

    # # Get all badges earned by a user
    # user = User.query.filter_by(username="JohnDoe").first()
    # if user:
    #     for badge in user.badges:
    #         print(f"Badge: {badge.name} - {badge.description}")

    # # Get all challenges that grant a specific badge
    # badge = Badge.query.filter_by(name="Elite Finisher").first()
    # if badge:
    #     for challenge in badge.challenges:
    #         print(f"Challenge: {challenge.title} grants the badge {badge.name}")

    # # Get all users who have completed a specific challenge
    # challenge = Challenge.query.filter_by(title="30-Day Fitness Challenge").first()
    # if challenge:
    #     completed_users = ChallengeParticipation.query.filter_by(challenge_id=challenge.id, is_completed=True).all()
    #     for participant in completed_users:
    #         print(f"User {participant.user.username} completed the challenge on {participant.completed_date}")

    # # Get all challenges that have no participants
    # challenges_without_participants = Challenge.query.filter(~Challenge.participations.any()).all()
    # for challenge in challenges_without_participants:
    #     print(f"Challenge: {challenge.title} has no participants yet.")

    # # Get the total number of challenges created by each user
    # user_challenge_counts = db.session.query(User.username, db.func.count(Challenge.id)).join(Challenge).group_by(User.id).all()
    # for username, count in user_challenge_counts:
    #     print(f"User {username} created {count} challenges")

    # # Find the user who has participated in the most challenges
    # most_active_user = db.session.query(User.username, db.func.count(ChallengeParticipation.id))\
    #     .join(ChallengeParticipation)\
    #     .group_by(User.id)\
    #     .order_by(db.func.count(ChallengeParticipation.id).desc())\
    #     .first()

    # if most_active_user:
    #     print(f"Most Active User: {most_active_user[0]} - Participated in {most_active_user[1]} challenges")
