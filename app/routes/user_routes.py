from flask import Blueprint, request, render_template, redirect, url_for, flash
# from app.models import db, User  ***Doesn't exist yet***

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return render_template('register.html', error="All fields are required.")

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return render_template('register.html', error="User already exists.")

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('users.login_user'))

    return render_template('register.html')


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return redirect(url_for('challenges.list_challenges'))
        return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')


@user_blueprint.route('/logout', methods=['GET'])
# @login_required   ***To be completed later***
def logout_user_route():
    """Logs out the current user."""
    # logout_user()  ***To be completed later***
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('users.login_user'))


@user_blueprint.route('/profile/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    created_challenges = user.challenges_created
    joined_challenges = user.challenge_participations
    return render_template('profile.html', user=user, created_challenges=created_challenges, joined_challenges=joined_challenges)
