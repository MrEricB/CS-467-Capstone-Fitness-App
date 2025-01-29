from flask import Blueprint, request, jsonify
from app.models import db, Challenge, ChallengeParticipation

challenge_blueprint = Blueprint('challenges', __name__)

# Get: List all challenges
@challenge_blueprint.route('/', methods=['GET'])
def list_challenges():
    challenges = Challenge.query.all()
    challenge_list = [
        {"id": challenge.id, "title": challenge.title, "description": challenge.description}
        for challenge in challenges
    ]
    return jsonify({"challenges": challenge_list}), 200


# POST: Create a new challenge
@challenge_blueprint.route('/create', methods=['GET', 'POST'])
def create_challenge():
    """Create a new challenge"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    if not title or not description:
        return jsonify({"error": "Title and description are required."}), 400

    new_challenge = Challenge(title=title, description=description)
    db.session.add(new_challenge)
    db.session.commit()

    return jsonify({
        "message": "Challenge created successfully.",
        "challenge": {"id": new_challenge.id, "title": new_challenge.title, "description": new_challenge.description}
    }), 201

# GET: Retrive a specific challenge
@challenge_blueprint.route('/<int:challenge_id>', methods=['GET'])
def challenge_details(challenge_id):
    """Get details of a specific challenge"""
    challenge = Challenge.query.get_or_404(challenge_id)

    return jsonify({
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description
    }), 200


# PUT: Update an existing challenge
@challenge_blueprint.route('/<int:challenge_id>', methods=['PUT'])
def update_challenge(challenge_id):
    """Update a challenge"""
    challenge = Challenge.query.get_or_404(challenge_id)
    data = request.get_json()

    challenge.title = data.get('title', challenge.title)
    challenge.description = data.get('description', challenge.description)

    db.session.commit()

    return jsonify({
        "message": "Challenge updated successfully.",
        "challenge": {"id": challenge.id, "title": challenge.title, "description": challenge.description}
    }), 200


# DELETE: Delete a challenge
@challenge_blueprint.route('/<int:challenge_id>', methods=['DELETE'])
def delete_challenge(challenge_id):
    """Delete a challenge"""
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()

    return jsonify({"message": "Challenge deleted successfully."}), 200


# POST: Join a challenge
@challenge_blueprint.route('/<int:challenge_id>/join', methods=['POST', 'GET'])
def join_challenge(challenge_id):
    """User joins a challenge"""
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required."}), 400

    challenge = Challenge.query.get_or_404(challenge_id)

    # Check if the user is already a participant
    participation = ChallengeParticipation.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()
    if participation:
        return jsonify({"error": "You have already joined this challenge."}), 400

    new_participation = ChallengeParticipation(user_id=user_id, challenge_id=challenge_id)
    db.session.add(new_participation)
    db.session.commit()

    return jsonify({"message": "Successfully joined the challenge."}), 201
