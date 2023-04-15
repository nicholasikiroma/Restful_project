from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TagModel, StoreModel, ItemModel
from schema import TagSchema, TagAndItemSchema

bp = Blueprint("Tags", "tags", description="Operations on tags")


@bp.route("/store/<string:store_id>/tag")
class TagInStore(MethodView):
    @bp.response(200, TagSchema(many=True))
    def get(self, store_id):
        """Fetch tags associated with a store"""
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @bp.arguments(TagSchema)
    @bp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        """Create tag in store"""
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400, message="Tag already exists in store.")

        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()

        except SQLAlchemyError as err:
            abort(500, message=str(err))

        return tag


@bp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @bp.response(200, TagSchema)
    def get(self, tag_id):
        """Fetch details about tag"""
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @bp.response(202,
                 description="Deletes a tag if no item s tagged with it.",
                 example={"message": "Tag deleted."})
    @bp.alt_response(404, description="Tag not found.")
    @bp.alt_response(400, description="Returned if tag is assigned to one or more items. In that case, tag is not deleted.")
    def delete(self, tag_id):
        """Delete Tag"""
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}

        abort(400, message="Could not delete tag. Make sure tag is not associated with any items, then try again.")


@bp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @bp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        "Link item to tag"
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()

        except SQLAlchemyError:
            abort(500, message="An error occured while inserting tag.")

        return tag

    @bp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        "Remove link between item and tag"
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()

        except SQLAlchemyError:
            abort(500, message="An error occured while removing tag.")

        return {"message": "Item removed from tag", "item": item,
                "tag": tag}
