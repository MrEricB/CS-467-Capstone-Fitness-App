from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

user_blueprint = Blueprint('users', __name__)


# POST: Register a new user
@user_blueprint.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register a new user"""
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "All fields are required."}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists."}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully.",
        "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    }), 201


# POST: Login user
@user_blueprint.route('/login', methods=['GET', 'POST'])
def login_user():
    """Authenticate user and return a session token"""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": "Login successful", "user": {"id": user.id, "username": user.username}}), 200

    return jsonify({"error": "Invalid username or password."}), 401

# GET: Logout user
@user_blueprint.route('/logout', methods=['GET'])
# @login_required   ***To be completed later***
def logout_user_route():
    """Logs out the current user."""
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


# GET: Retrieve user profile
@user_blueprint.route('/profile/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    """Retrieve the authenticated user's profile"""
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }), 200

# PUT: Update user details
@user_blueprint.route('/update', methods=['PUT'])
@login_required
def update_user():
    """Update the authenticated user's details"""
    data = request.get_json()

    if "username" in data:
        current_user.username = data['username']
    if "email" in data:
        current_user.email = data['email']
    
    db.session.commit()

    return jsonify({
        "message": "User updated successfully.",
        "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email}
    }), 200

# DELETE: Delete user account
@user_blueprint.route('/delete', methods=['DELETE'])
@login_required
def delete_user():
    """Delete the authenticated user's account"""
    db.session.delete(current_user)
    db.session.commit()

    return jsonify({"message": "User account deleted successfully"}), 200
