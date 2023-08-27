from flask import Flask
from config import DevConfig, ProConfig, TestConfig
from exts import db, marshmallow, migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from blueprints.query_route import query_bp
from blueprints.auth_routes import auth_bp
from blueprints.sentiment_analysis_routes import sentiment_bp


def create_app():
    app = Flask(__name__)
    if app.config.get("ENV") == "production":
        app.config.from_object(ProConfig)
    elif app.config.get("ENV") == "testing":
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevConfig)
    with app.app_context():
        CORS(app)
        Bcrypt(app)
        JWTManager(app)
        marshmallow.init_app(app)
        db.init_app(app)
        migrate.init_app(app, db)
        app.register_blueprint(auth_bp)
        app.register_blueprint(query_bp)
        app.register_blueprint(sentiment_bp)

    return app
