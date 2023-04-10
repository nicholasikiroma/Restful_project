"""Defines endpoints and for fetching, updating, and deleting items"""
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schema import ItemSchema, ItemUpdateSchema

# Initialize module as blueprint
bp = Blueprint("items", __name__, description="Operations on items")


@bp.route("/item")
class ItemList(MethodView):
    @bp.response(200, ItemSchema(many=True))
    def get(self):
        """Returns all items in stores"""
        items = ItemModel.query.all()
        return items

    @bp.arguments(ItemSchema)
    @bp.response(201, ItemSchema)
    def post(self, item_data):
        """Updates an item/create item"""
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()

        except SQLAlchemyError:
            abort(500, message="An error occured while creating item.")

        return item


@bp.route("/item/<string:item_id>")
class Item(MethodView):
    @bp.response(200, ItemSchema)
    def get(self, item_id):
        """Get an item"""
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id):
        """Delete an item"""
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()

        return {"messgae": "Item deleted"}
    
    @bp.arguments(ItemUpdateSchema)
    @bp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        "Update item in store"
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]

        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item
