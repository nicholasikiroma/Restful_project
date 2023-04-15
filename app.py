import os

from flask import Flask
from flask_smorest import Api

from db import db
import models

from resources.store import bp as store_bp
from resources.item import bp as item_bp
from resources.tag import bp as tag_bp


def create_app(db_url=None):

    # create instance of flask app
    app = Flask(__name__)

    # base configurations for flask app
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "STORES REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialise database
    db.init_app(app)

     # Initialise SMOREST
    api = Api(app)

    # creates tables before handling requests
    @app.before_first_request
    def create_tables():
        db.create_all()

    # Registering item and store blueprints
    api.register_blueprint(item_bp)
    api.register_blueprint(store_bp)
    api.register_blueprint(tag_bp)

    return app