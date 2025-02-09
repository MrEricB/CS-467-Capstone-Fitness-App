import os
from flask import Flask
from models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)


    # UPLOAD_FOLDER = os.path.join('static', 'uploads')
    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # BADGES_FOLDER = os.path.join('static', 'badges')
    # app.config['BADGES_FOLDER'] = BADGES_FOLDER

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BADGES_FOLDER'], exist_ok=True)



    # Register Blueprints
    from routes.challenge_routes import challenge_bp
    from routes.user_routes import user_bp

    app.register_blueprint(challenge_bp)
    app.register_blueprint(user_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
