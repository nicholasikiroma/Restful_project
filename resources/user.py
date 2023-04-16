"""Module contains code for user blueprint"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from db import db
from models import UserModel
from schema import UserSchema

bp = Blueprint("Users", "users", description="\
               Operations on users")


@bp.route('/user/<int:user_id>')
class Users(MethodView):

    @bp.response(200, UserSchema)
    def get(self, user_id):
        """Fetch User"""
        user = UserModel.query.get_or_404(user_id)
        return user

    @bp.response(200)
    def delete(self, user_id):
        """Delete User"""
        user = UserModel.query.get_or_404(user_id)

        try:
            db.session.delete(user)
            db.session.commit()

        except SQLAlchemyError as err:
            abort(500, message=f"{err}")

        return {"message": "user deleted"}


@bp.route('/register')
class RegisterUser(MethodView):
    @bp.arguments(UserSchema)
    def post(self, user_data):
        """Creates user"""

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )

        try:
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            abort(400, message="User already exists")

        except SQLAlchemyError as err:
            abort(500, message=f"{err}")

        return {"message": "User created successfully."}, 201


@bp.route('/login')
class UserLogin(MethodView):

    @bp.arguments(UserSchema)
    def post(self, user_data):
        """Login users"""
        user = UserModel.query.filter(
            UserModel.username == user_data['username']).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}

        abort(401, message="Invalid credentials.")


@bp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]

        from app import jwt_redis_blocklist, ACCESS_EXPIRES
        jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
        return {"message": "Successfully logged out."}
