import os
from datetime import timedelta

import redis
import idna

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
import models

from resources.store import bp as store_bp
from resources.item import bp as item_bp
from resources.tag import bp as tag_bp
from resources.user import bp as user_bp

hostname = idna.encode("rediss://red-cguhiqt269vbmerpe7i0:xlK6CqF2vuGYWDT8ax7DiCOdVzwh8SC9@oregon-redis.render.com").decode("utf-8")
# Set up redis connection
# host is the ip of a standalone docker
# container running redis
jwt_redis_blocklist = redis.StrictRedis(
    host=hostname,
    port=6379, db=0,
    decode_responses=True
)

# Set expiration for jwt token
ACCESS_EXPIRES = timedelta(minutes=30)


def create_app(db_url=None):

    # create instance of flask app
    app = Flask(__name__)

    # access env file
    load_dotenv()

    # base configurations for flask app
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "STORES REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES

    # Initialise database
    db.init_app(app)

    # Initialise SMOREST
    api = Api(app)

    # Initialise JWT
    jwt = JWTManager(app)

    # Initialise flask migrate
    migrate = Migrate(app, db)

    # Logout handler
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    # Custom error messages for JWT
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "message": "The token has been revoked.",
                "error": "token_revoked"
            }), 401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "message": "The token has expired",
                "error": "token_expired"
            }), 401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({
                "message": "Signature verification failed",
                "error": "invalid_token"
            }), 401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({
                "message": "Request does not contain an access token.",
                "error": "authorization_required"
            }), 401,
        )

    # Registering item and store blueprints
    api.register_blueprint(item_bp)
    api.register_blueprint(store_bp)
    api.register_blueprint(tag_bp)
    api.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()

    return app
