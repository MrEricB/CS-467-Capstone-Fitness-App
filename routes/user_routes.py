from flask import Blueprint, render_template, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Favorite
from forms import RegistrationForm, LoginForm

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose another.')
            return render_template('register.html', form=form)
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('user_bp.login'))
    return render_template('register.html', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully.')
            return redirect(url_for('challenge_bp.index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@user_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('challenge_bp.index'))

@user_bp.route('/favorites')
def favorites():
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('user_bp.login'))
    
    favs = Favorite.query.filter_by(user_id=session['user_id']).all()
    challenges = [fav.challenge for fav in favs]
    
    return render_template('favorites.html', challenges=challenges)
