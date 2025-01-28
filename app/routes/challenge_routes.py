from flask import Blueprint, render_template, request
# from app.models import db, Challenge  ***Doesn't exist yet***

challenge_blueprint = Blueprint('challenges', __name__)

@challenge_blueprint.route('/', methods=['GET'])
def list_challenges():
    challenges = Challenge.query.all()
    return render_template('home.html', challenges=challenges)


@challenge_blueprint.route('/create', methods=['GET', 'POST'])
def create_challenge():
    if request.method == 'POST':
        data = request.form
        title = data.get('title')
        description = data.get('description')

        if not title or not description:
            return render_template('create_challenge.html', error="Title and description are required.")

        new_challenge = Challenge(title=title, description=description)
        db.session.add(new_challenge)
        db.session.commit()

        return redirect(url_for('challenges.list_challenges'))

    return render_template('create_challenge.html')

@challenge_blueprint.route('/<int:challenge_id>', methods=['GET'])
def challenge_details(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    return render_template('challenge_details.html', challenge=challenge)


@challenge_blueprint.route('/<int:challenge_id>/join', methods=['POST', 'GET'])
def join_challenge(challenge_id):
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        challenge = Challenge.query.get_or_404(challenge_id)

        # Check if the user is already a participant
        participation = ChallengeParticipation.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()
        if participation:
            return render_template('challenge_details.html', challenge=challenge, error="You have already joined this challenge.")

        # Add user as a participant
        new_participation = ChallengeParticipation(user_id=user_id, challenge_id=challenge_id)
        db.session.add(new_participation)
        db.session.commit()

        return render_template('challenge_details.html', challenge=challenge, success="You have successfully joined the challenge.")

    challenge = Challenge.query.get_or_404(challenge_id)
    return render_template('challenge_details.html', challenge=challenge)
