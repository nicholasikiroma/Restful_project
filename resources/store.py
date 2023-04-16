"""Defines endpoints and for fetching and deleting stores"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schema import StoreSchema

# Initialise module as blueprint
bp = Blueprint("stores", __name__, description="Operations on stores")


@bp.route("/store/<int:store_id>")
class Store(MethodView):
    @bp.response(200, StoreSchema)
    def get(self, store_id):
        """Get a store"""
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required()
    def delete(self, store_id):
        """Delete a store"""
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return {"messgae": "store deleted"}


@bp.route("/store")
class StoreList(MethodView):
    @bp.response(200, StoreSchema(many=True))
    def get(self):
        """Returns all stores"""
        store = StoreModel.query.all()
        return store

    @jwt_required()
    @bp.arguments(StoreSchema)
    @bp.response(201, StoreSchema)
    def post(self, store_data):
        """Create a store"""
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()

        except IntegrityError:
            abort(400, message="Store with that name already exists.")

        except SQLAlchemyError:
            abort(500, message="An error occured while creating store.")

        return store
