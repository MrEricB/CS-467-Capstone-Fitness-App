from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from werkzeug.utils import secure_filename
import os
from models import db, Challenge, Goal, ChallengeBadge, CompletedChallenge, UserChallengeStatus, ChatMessage
from forms import ChallengeForm, ChatForm

challenge_bp = Blueprint('challenge_bp', __name__)

@challenge_bp.route('/')
def index():
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    user_badges = []

    if session.get('user_id'):
        completed_chals = CompletedChallenge.query.filter_by(user_id=session['user_id']).all()
        for comp in completed_chals:
            challenge_obj = Challenge.query.get(comp.challenge_id)
            if challenge_obj and challenge_obj.badges:
                for badge in challenge_obj.badges:
                    user_badges.append(badge.badge)
        user_badges = list(set(user_badges))

    return render_template('index.html', challenges=challenges, user_badges=user_badges)

@challenge_bp.route('/create', methods=['GET', 'POST'])
def create_challenge():
    if 'user_id' not in session:
        flash('Please log in to create a challenge.')
        return redirect(url_for('user_bp.login'))

    form = ChallengeForm()

    # Populate badge choices dynamically from badge folder
    badges_folder_path = os.path.join(current_app.root_path, current_app.config['BADGES_FOLDER'])
    available_badges = []
    if os.path.exists(badges_folder_path):
        for filename in os.listdir(badges_folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                available_badges.append((filename, filename))
    form.badges.choices = available_badges

    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))

        new_challenge = Challenge(
            user_id=session['user_id'],
            challenge_type=form.challenge_type.data,
            image=image_filename,
            description=form.description.data,
            tags=form.tags.data
        )
        db.session.add(new_challenge)
        db.session.commit()

        for goal_text in form.goals.data.strip().splitlines():
            new_goal = Goal(challenge_id=new_challenge.id, goal_text=goal_text)
            db.session.add(new_goal)

        for badge in form.badges.data:
            new_badge = ChallengeBadge(challenge_id=new_challenge.id, badge=badge)
            db.session.add(new_badge)

        db.session.commit()
        flash('Challenge created successfully!')
        return redirect(url_for('challenge_bp.challenge_detail', challenge_id=new_challenge.id))

    return render_template('create_challenge.html', form=form, available_badges=available_badges)

@challenge_bp.route('/<int:challenge_id>', methods=['GET'])
def challenge_detail(challenge_id):
    challenge_obj = Challenge.query.get(challenge_id)
    if not challenge_obj:
        flash('Challenge not found.')
        return redirect(url_for('challenge_bp.index'))

    goals = Goal.query.filter_by(challenge_id=challenge_id).all()
    chat_messages = ChatMessage.query.filter_by(challenge_id=challenge_id).order_by(ChatMessage.timestamp.asc()).all()

    completed_goal_ids = []
    if session.get('user_id'):
        statuses = UserChallengeStatus.query.filter_by(
            user_id=session['user_id'],
            challenge_id=challenge_id,
            is_complete=True
        ).all()
        completed_goal_ids = [status.goal_id for status in statuses]

    is_completed = False
    if session.get('user_id'):
        if CompletedChallenge.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first():
            is_completed = True

    chat_form = ChatForm()

    return render_template('challenge_detail.html',
                           challenge=challenge_obj,
                           goals=goals,
                           chat_messages=chat_messages,
                           completed_goal_ids=completed_goal_ids,
                           is_completed=is_completed,
                           chat_form=chat_form)

@challenge_bp.route('/<int:challenge_id>/chat', methods=['POST'])
def chat(challenge_id):
    if 'user_id' not in session:
        flash('Please log in to participate in chat.')
        return redirect(url_for('user_bp.login'))

    form = ChatForm()
    if form.validate_on_submit():
        image_filename = None
        if form.chat_image.data:
            image_filename = secure_filename(form.chat_image.data.filename)
            form.chat_image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))

        new_message = ChatMessage(
            challenge_id=challenge_id,
            user_id=session['user_id'],
            message=form.message.data,
            image=image_filename
        )
        db.session.add(new_message)
        db.session.commit()
    else:
        flash("There was an error with your chat message.")

    return redirect(url_for('challenge_bp.challenge_detail', challenge_id=challenge_id))

@challenge_bp.route('/<int:challenge_id>/complete_goal/<int:goal_id>')
def complete_goal(challenge_id, goal_id):
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('user_bp.login'))

    status = UserChallengeStatus.query.filter_by(
        user_id=session['user_id'],
        challenge_id=challenge_id,
        goal_id=goal_id
    ).first()

    if status:
        status.is_complete = True
    else:
        status = UserChallengeStatus(
            user_id=session['user_id'],
            challenge_id=challenge_id,
            goal_id=goal_id,
            is_complete=True
        )
        db.session.add(status)

    db.session.commit()
    flash('Goal marked as complete!')
    return redirect(url_for('challenge_bp.challenge_detail', challenge_id=challenge_id))

@challenge_bp.route('/<int:challenge_id>/complete', methods=['POST'])
def complete_challenge(challenge_id):
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('user_bp.login'))

    if not CompletedChallenge.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first():
        comp = CompletedChallenge(user_id=session['user_id'], challenge_id=challenge_id)
        db.session.add(comp)
        db.session.commit()
        flash('Challenge completed! You are now on the Wall of Fame.')

    return redirect(url_for('challenge_bp.challenge_detail', challenge_id=challenge_id))
