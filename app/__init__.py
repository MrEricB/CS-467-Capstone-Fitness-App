from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from app.routes.user_routes import user_blueprint
    from app.routes.challenge_routes import challenge_blueprint
    # To be completed at a later date
    # from app.routes.media_routes import media_blueprint
    # from app.routes.social_routes import social_blueprint

    app.register_blueprint(user_blueprint, url_prefix='/users')
    app.register_blueprint(challenge_blueprint, url_prefix='/challenges')
    # app.register_blueprint(media_blueprint, url_prefix='/media')
    # app.register_blueprint(social_blueprint, url_prefix='/social')

    return app
