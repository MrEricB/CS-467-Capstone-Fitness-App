from app import app
from flask import render_template


@app.route('/')
@app.route('/home')
def homepage():
    return render_template('homepage.html', title='Home Page')


@app.route('/register')
def register():
    return render_template('register.html', title='Register')


@app.route('/login')
def login():
    return render_template('login.html', title='Login')


@app.route('/logout')
def logout():
    return render_template('logout.html', title='Logout')


@app.route('/profile')
def profile():
    return render_template('profile.html', title='Profile')


@app.route('/createchallenge')
def create_challenge():
    return render_template('createchallenge.html', title='Create Challenge')


@app.route('/viewchallenge')
def view_challenge():
    return render_template('viewchallenge.html', title='View Challenge')


@app.route('/searchchallenges')
def search_challenges():
    return render_template('searchchallenges.html', title='Search Challenges')


@app.route('/viewallchallenges')
def view_all_challenges():
    return render_template('viewallchallenges.html',
                           title='View All Challenges')
