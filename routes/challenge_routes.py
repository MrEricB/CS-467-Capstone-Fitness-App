import os
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.utils import secure_filename
from models import db, Challenge, Goal, ChallengeBadge, ChatMessage, UserChallengeStatus, CompletedChallenge, Favorite
from forms import ChallengeForm, ChatForm
from flask import current_app

challenge_bp = Blueprint('challenge_bp', __name__)

@challenge_bp.route('/')
def index():
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    user_badges = []
    completed_challenge_ids = []
    if session.get('user_id'):
        # Gather badges from any completed challenges (for display purposes)
        completed_chals = CompletedChallenge.query.filter_by(user_id=session['user_id']).all()
        for comp in completed_chals:
            challenge_obj = Challenge.query.get(comp.challenge_id)
            if challenge_obj and challenge_obj.badges:
                for badge in challenge_obj.badges:
                    user_badges.append(badge.badge)
        user_badges = list(set(user_badges))
        
        # Get IDs of challenges the user has marked as completed (regardless of full completion)
        completed_challenge_ids = [comp.challenge_id for comp in CompletedChallenge.query.filter_by(user_id=session['user_id']).all()]
    
    return render_template('index.html', challenges=challenges, user_badges=user_badges, completed_challenge_ids=completed_challenge_ids)

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
        return redirect(url_for('challenge_bp.challenge', challenge_id=new_challenge.id))

    return render_template('create_challenge.html', form=form, available_badges=available_badges)

@challenge_bp.route('/<int:challenge_id>', methods=['GET'])
def challenge(challenge_id):
    challenge_obj = Challenge.query.get(challenge_id)
    if not challenge_obj:
        flash('Challenge not found.')
        return redirect(url_for('challenge_bp.index'))

    goals = Goal.query.filter_by(challenge_id=challenge_id).all()
    chat_messages = ChatMessage.query.filter_by(challenge_id=challenge_id).order_by(ChatMessage.timestamp.asc()).all()

    completed_goal_ids = []
    is_favorited = False  # Default value
    if session.get('user_id'):
        # Determine completed goals
        statuses = UserChallengeStatus.query.filter_by(
            user_id=session['user_id'],
            challenge_id=challenge_id,
            is_complete=True
        ).all()
        completed_goal_ids = [status.goal_id for status in statuses]
        # Check if this challenge is favorited by the user
        favorite = Favorite.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first()
        if favorite:
            is_favorited = True

    is_completed = False
    if session.get('user_id'):
        if CompletedChallenge.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first():
            is_completed = True

    chat_form = ChatForm()

    return render_template('challenge.html',
                           challenge=challenge_obj,
                           goals=goals,
                           chat_messages=chat_messages,
                           completed_goal_ids=completed_goal_ids,
                           is_completed=is_completed,
                           is_favorited=is_favorited,
                           chat_form=chat_form)

@challenge_bp.route('/challenge/<int:challenge_id>/chat', methods=['POST'])
def chat(challenge_id):
    if 'user_id' not in session:
        flash('Please log in to participate in chat.')
        return redirect(url_for('login'))
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

    return redirect(url_for('challenge_bp.challenge', challenge_id=challenge_id))

# @challenge_bp.route('/<int:challenge_id>/complete', methods=['POST'])
# def complete_challenge(challenge_id):
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('user_bp.login'))

    user_id = session['user_id']
    
    # Get all goals for the challenge
    goal_ids = {goal.id for goal in Goal.query.filter_by(challenge_id=challenge_id).all()}

    # Get completed goals for the user
    completed_goal_ids = {status.goal_id for status in UserChallengeStatus.query.filter_by(
        user_id=user_id, challenge_id=challenge_id, is_complete=True).all()}

    # **NEW LOGIC**: Challenge is considered complete if at least one goal is completed
    has_completed_any_goal = bool(completed_goal_ids)

    if has_completed_any_goal:
        # Check if the challenge is already marked as completed
        comp = CompletedChallenge.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()

        if not comp:
            comp = CompletedChallenge(user_id=user_id, challenge_id=challenge_id, fully_completed=(goal_ids == completed_goal_ids))
            db.session.add(comp)
        else:
            comp.fully_completed = (goal_ids == completed_goal_ids)  # Still track if fully completed

        db.session.commit()

        flash('Challenge marked as completed! Keep going to complete all goals for Wall of Fame.')

    else:
        flash('Complete at least one goal to complete this challenge.')

    return redirect(url_for('challenge_bp.challenge', challenge_id=challenge_id, confetti='false'))
@challenge_bp.route('/<int:challenge_id>/complete', methods=['POST'])
def complete_challenge(challenge_id):
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('user_bp.login'))

    user_id = session['user_id']
    
    # Get all goals for the challenge
    goal_ids = {goal.id for goal in Goal.query.filter_by(challenge_id=challenge_id).all()}

    # Get completed goals for the user
    completed_goal_ids = {status.goal_id for status in UserChallengeStatus.query.filter_by(
        user_id=user_id, challenge_id=challenge_id, is_complete=True).all()}

    has_completed_any_goal = bool(completed_goal_ids)

    if has_completed_any_goal:
        # Check if the challenge is already marked as completed
        comp = CompletedChallenge.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()

        if not comp:
            # First time completion – mark as complete and add confetti flag
            comp = CompletedChallenge(
                user_id=user_id, 
                challenge_id=challenge_id, 
                fully_completed=(goal_ids == completed_goal_ids)
            )
            db.session.add(comp)
            db.session.commit()
            flash('Challenge marked as completed! Keep going to complete all goals for Wall of Fame.')
            return redirect(url_for('challenge_bp.challenge', challenge_id=challenge_id, confetti='true'))
        else:
            # Already completed – just update if necessary and don't trigger confetti
            comp.fully_completed = (goal_ids == completed_goal_ids)
            db.session.commit()
            flash('Challenge already marked as completed.')
    else:
        flash('Complete at least one goal to complete this challenge.')

    return redirect(url_for('challenge_bp.challenge', challenge_id=challenge_id))

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
    return redirect(url_for('challenge_bp.challenge', challenge_id=challenge_id))

# Wall of Fame for a specific challenge - only show if fully completed
@challenge_bp.route('/<int:challenge_id>/wall_of_fame')
def wall_of_fame(challenge_id):
    challenge_obj = Challenge.query.get(challenge_id)
    if not challenge_obj:
        flash('Challenge not found.')
        return redirect(url_for('challenge_bp.index'))
    
    wall_entries = CompletedChallenge.query.filter_by(challenge_id=challenge_id, fully_completed=True)\
                    .order_by(CompletedChallenge.completed_at.desc()).all()
    return render_template('challenge_wall_of_fame.html', wall_entries=wall_entries, challenge=challenge_obj)

@challenge_bp.route('/search')
def search():
    query = request.args.get('query', '')
    challenges = Challenge.query.filter(Challenge.tags.contains(query)).all()
    return render_template('index.html', challenges=challenges)

@challenge_bp.route('/<int:challenge_id>/favorite', methods=['POST'])
def add_to_favorites(challenge_id):
    if 'user_id' not in session:
        flash('Please log in to favorite challenges.')
        return redirect(url_for('user_bp.login'))

    existing_fav = Favorite.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first()
    if not existing_fav:
        favorite = Favorite(user_id=session['user_id'], challenge_id=challenge_id)
        db.session.add(favorite)
        db.session.commit()
        flash('Added to favorites!')
    else:
        flash('Challenge is already in your favorites.')

    return redirect(url_for('challenge_bp.challenge', challenge_id=challenge_id))

@challenge_bp.route('/<int:challenge_id>/unfavorite', methods=['POST'])
def remove_from_favorites(challenge_id):
    if 'user_id' not in session:
        flash('Please log in to manage favorites.')
        return redirect(url_for('user_bp.login'))

    favorite = Favorite.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash('Removed from favorites.')
    else:
        flash('Challenge was not in your favorites.')

    return redirect(url_for('challenge_bp.challenge', challenge_id=challenge_id))