from flask_smorest import Blueprint, abort
from flask.views import MethodView


from db import db
from models import TagModel, StoreModel
from schema import TagSchema

bp = Blueprint("Tags", "tags", description="Operations on tags")


@bp.route("/store/<string:store_id>/tag")
class TagInStore(MethodView):
    @bp.response(200, TagSchema(many=True))
    def get(self, store_id):
        pass