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

# ---------------------------
# Index Route
# ---------------------------
@app.route('/')
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

# ---------------------------
# Registration Route using Flask Forms
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose another.')
            return render_template('register.html', form=form)
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data,
                        email=form.email.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# ---------------------------
# Login Route using Flask Forms
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

# ---------------------------
# Logout Route
# ---------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

# ---------------------------
# Create Challenge Route using Flask Forms
# ---------------------------
@app.route('/create_challenge', methods=['GET', 'POST'])
def create_challenge():
    if 'user_id' not in session:
        flash('Please log in to create a challenge.')
        return redirect(url_for('login'))
    
    form = ChallengeForm()
    
    # grab avliable bagges from static folder
    badges_folder_path = os.path.join(app.root_path, app.config['BADGES_FOLDER'])
    available_badges = []
    if os.path.exists(badges_folder_path):
        for filename in os.listdir(badges_folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                available_badges.append((filename, filename))
    form.badges.choices = available_badges

    # flask forms
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            
        new_challenge = Challenge(
            user_id=session['user_id'],
            challenge_type=form.challenge_type.data,
            image=image_filename,
            description=form.description.data,
            tags=form.tags.data
        )
        db.session.add(new_challenge)
        db.session.commit()  # Commit to generate the challenge ID

        # Insert goals into db
        for goal_text in form.goals.data.strip().splitlines():
            new_goal = Goal(challenge_id=new_challenge.id, goal_text=goal_text)
            db.session.add(new_goal)
        
        # Insert the badges select as filname
        for badge in form.badges.data:
            new_badge = ChallengeBadge(challenge_id=new_challenge.id, badge=badge)
            db.session.add(new_badge)
        
        db.session.commit()
        flash('Challenge created successfully!')
        return redirect(url_for('challenge', challenge_id=new_challenge.id))
    
    return render_template('create_challenge.html', form=form, available_badges=available_badges)

# ---------------------------
# Challenge Detail Route
# TODO: still need to flush out and finish user adding challenge to their favorits
# ---------------------------
@app.route('/challenge/<int:challenge_id>', methods=['GET'])
def challenge(challenge_id):
    challenge_obj = Challenge.query.get(challenge_id)
    if not challenge_obj:
        flash('Challenge not found.')
        return redirect(url_for('index'))
    
    goals = Goal.query.filter_by(challenge_id=challenge_id).all()
    chat_messages = ChatMessage.query.filter_by(challenge_id=challenge_id)\
                        .order_by(ChatMessage.timestamp.asc()).all()
    
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

    # create a ChatForm for the chat posting section done via flask forms
    chat_form = ChatForm()

    # Check if the challenge is favorited by the current user
    # NOTE Note full implemented
    # TODO
    is_favorited = False
    if session.get('user_id'):
        fav = Favorite.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first()
        if fav:
            is_favorited = True

    return render_template('challenge.html',
                           challenge=challenge_obj,
                           goals=goals,
                           chat_messages=chat_messages,
                           completed_goal_ids=completed_goal_ids,
                           is_completed=is_completed,
                           chat_form=chat_form,
                           is_favorited=is_favorited)

# ---------------------------
# Post a Chat Message using Flask Forms
# ---------------------------
@app.route('/challenge/<int:challenge_id>/chat', methods=['POST'])
def chat(challenge_id):
    if 'user_id' not in session:
        flash('Please log in to participate in chat.')
        return redirect(url_for('login'))
    form = ChatForm()
    if form.validate_on_submit():
        image_filename = None
        if form.chat_image.data:
            image_filename = secure_filename(form.chat_image.data.filename)
            form.chat_image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
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
    return redirect(url_for('challenge', challenge_id=challenge_id))

# ---------------------------
# Mark a Goal as Complete
# ---------------------------
@app.route('/challenge/<int:challenge_id>/complete_goal/<int:goal_id>')
def complete_goal(challenge_id, goal_id):
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('login'))
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
    return redirect(url_for('challenge', challenge_id=challenge_id))


# ---------------------------
# Complete Entire Challenge (if all goals done, remove and allow completion with out finishing all goals, may complete all goasl gets you on the wall of fame for that challenge?
#TODO: bugs and issues with marking as complete and getting in the wall of fame even if user has not complete all goals
# ---------------------------
# @app.route('/challenge/<int:challenge_id>/complete', methods=['POST'])
# def complete_challenge(challenge_id):
#     if 'user_id' not in session:
#         flash('Please log in.')
#         return redirect(url_for('login'))
#     total_goals = Goal.query.filter_by(challenge_id=challenge_id).count()
#     completed = UserChallengeStatus.query.filter_by(
#         user_id=session['user_id'],
#         challenge_id=challenge_id,
#         is_complete=True
#     ).count()
#     if completed < total_goals:
#         flash('Please complete all goals before completing the challenge.')
#         return redirect(url_for('challenge', challenge_id=challenge_id))
    
#     if not CompletedChallenge.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first():
#         comp = CompletedChallenge(user_id=session['user_id'], challenge_id=challenge_id)
#         db.session.add(comp)
#         db.session.commit()
#         flash('Challenge completed! You are now on the Wall of Fame.')
#     return redirect(url_for('challenge', challenge_id=challenge_id))

## ALternate
@app.route('/challenge/<int:challenge_id>/complete', methods=['POST'])
def complete_challenge(challenge_id):
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('login'))
    ## NOTE:
    ## REMOVE to allow users to complete challenge without having to meet all the goals
    ## then people who complete all the goals can be in the wall of fame

    # total_goals = Goal.query.filter_by(challenge_id=challenge_id).count()
    # completed = UserChallengeStatus.query.filter_by(
    #     user_id=session['user_id'],
    #     challenge_id=challenge_id,
    #     is_complete=True
    # ).count()
    # if completed < total_goals:
    #     flash('Please complete all goals before completing the challenge.')
    #     return redirect(url_for('challenge', challenge_id=challenge_id))
    
    if not CompletedChallenge.query.filter_by(user_id=session['user_id'], challenge_id=challenge_id).first():
        comp = CompletedChallenge(user_id=session['user_id'], challenge_id=challenge_id)
        db.session.add(comp)
        db.session.commit()
        flash('Challenge completed! You are now on the Wall of Fame.')
    else:
        flash('You have completed this challenge!')
    return redirect(url_for('challenge', challenge_id=challenge_id))




# ---------------------------
# Wall of Fame Route
# NOTE: Maybe change the wall of fame to be the owned by the challegned and users who complete the challenge and all its goals are added here.
# ---------------------------
@app.route('/wall_of_fame')
def wall_of_fame():
    wall_entries = CompletedChallenge.query.order_by(CompletedChallenge.completed_at.desc()).all()
    print(wall_entries)
    return render_template('wall_of_fame.html', wall_entries=wall_entries)
# Alternate using note above
@app.route('/challenge/<int:challenge_id>/wall_of_fame')
def challenge_wall_of_fame(challenge_id):
    # Retrieve the challenge by its ID.
    challenge_obj = Challenge.query.get(challenge_id)
    if not challenge_obj:
        flash('Challenge not found.')
        return redirect(url_for('index'))
    
    # Query CompletedChallenge records for this specific challenge.
    wall_entries = CompletedChallenge.query.filter_by(challenge_id=challenge_id).order_by(CompletedChallenge.completed_at.desc()).all()
    
    # Render the wall of fame template with the challenge and its completions.
    return render_template('challenge_wall_of_fame.html', challenge=challenge_obj, wall_entries=wall_entries)


# ---------------------------
# Favorites Route
# NOTE: not implemented or tested yet
# ---------------------------
@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('login'))
    favs = Favorite.query.filter_by(user_id=session['user_id']).all()
    challenges = [fav.challenge for fav in favs]
    return render_template('favorites.html', challenges=challenges)

# ---------------------------
# Search Route
# NOTE: not implemented or tested yet
# ---------------------------
@app.route('/search')
def search():
    query = request.args.get('query', '')
    challenges = Challenge.query.filter(Challenge.tags.contains(query)).all()
    return render_template('index.html', challenges=challenges)

if __name__ == '__main__':
    app.run(debug=True)
