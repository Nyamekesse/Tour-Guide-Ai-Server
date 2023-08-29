from flask import request, jsonify, make_response, Blueprint
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from errors import (
    handle_bad_request,
    handle_conflict_error,
    handle_internal_server_error,
    handle_not_found,
    handle_not_processable_error,
)
from decouple import config

from models.user import User

MULTI_AVATAR_API_KEY = config("MULTI_AVATAR_API_KEY")

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


def avatar_generator(name):
    avatar = f"https://api.multiavatar.com/{name}.svg?apikey={MULTI_AVATAR_API_KEY}"
    return avatar


@auth_bp.route("/signup", methods=["POST"])
def create_user():
    """create a new user"""
    data = request.get_json()

    if not data:
        return handle_not_processable_error("")
    existing_user = User.objects(email=data["email"]).first()
    if existing_user:
        return handle_conflict_error("User with given email address already exists.")
    else:
        try:
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            role = data.get("role")

            new_user = User(
                name=username,
                email=email,
                password=generate_password_hash(password).decode("utf-8"),
                display_picture=avatar_generator(username),
                role=role,
            )
            new_user.save()
            new_user = new_user.to_mongo().to_dict()
            new_user["_id"] = str(new_user["_id"])
            del new_user["password"]
            return make_response(
                jsonify(
                    {
                        "success": True,
                        "message": "User successfully created",
                        "user": new_user,
                    }
                ),
                201,
            )
        except Exception as e:
            print(e)
            return handle_internal_server_error(
                "Something went wrong please try again later"
            )


@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    if data is None:
        return handle_not_processable_error("")
    try:
        email_or_name = data.get("usernameOrEmail").strip()
        password = data.get("password").strip()

        user = (
            User.objects(email=email_or_name).first()
            or User.objects(name=email_or_name).first()
        )

        if user and check_password_hash(user.password, password):
            user = user.to_mongo().to_dict()
            user["_id"] = str(user["_id"])
            del user["password"]
            user_identity = {"id": user["_id"], "role": user["role"]}

            access_token = create_access_token(identity=user_identity, fresh=True)
            refresh_token = create_refresh_token(identity=user_identity)
            headers = {"Authorization": "Bearer {}".format(access_token)}
            response = make_response(
                jsonify(
                    {
                        "success": True,
                        "message": "Login successful",
                        "profile": user,
                        "token": access_token,
                    }
                ),
                200,
                headers,
            )

            return response
        return handle_not_found("")

    except Exception as e:
        print(e)
        return handle_internal_server_error(
            "something went wrong please try again later"
        )
