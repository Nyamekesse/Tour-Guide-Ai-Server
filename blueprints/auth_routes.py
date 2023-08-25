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
    handle_internal_server_error,
    handle_not_found,
    handle_not_processable_error,
)
from decouple import config
from sqlalchemy.orm.exc import NoResultFound
from models.user import User, user_schema

MULTI_AVATAR_API_KEY = config("MULTI_AVATAR_API_KEY")

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


def is_username_or_email_taken(username, email):
    user = User.query.filter(
        (User.username == username) | (User.user_email == email)
    ).first()
    return user is not None


def avatar_generator(name):
    avatar = f"https://api.multiavatar.com/{name}.svg?apikey={MULTI_AVATAR_API_KEY}"
    return avatar


@auth_bp.route("/signup", methods=["POST"])
def create_user():
    """create a new user"""
    data = request.get_json()

    if not data:
        return handle_not_processable_error("")
    else:
        try:
            username = data.get("username")
            user_email = data.get("email")
            password = data.get("password")
            confirm_password = data.get("confirmPassword")

            if is_username_or_email_taken(username, user_email):
                return handle_not_processable_error("Username or Email already exist")

            if confirm_password != password:
                return handle_bad_request("Passwords must match")
            new_user = User(
                username=username,
                display_picture=avatar_generator(username),
                user_email=user_email,
                password=generate_password_hash(password).decode("utf-8"),
            )
            new_user.insert()
            new_user = user_schema.dump(new_user)
            return make_response(
                jsonify(
                    {
                        "success": True,
                        "message": "User successfully created",
                        "new_author_id": new_user.get("id"),
                        "new_username": new_user.get("username"),
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
        username_or_email = data.get("usernameOrEmail").strip()
        password = data.get("password").strip()

        user = User.query.filter(
            (User.user_email == username_or_email)
            | (User.username == username_or_email)
        ).one()

        if user and check_password_hash(user.password, password):
            user_identity = {"id": user.id, "role": user.role}
            profile = {
                "username": user.username,
                "user_email": user.user_email,
                "display_picture": user.display_picture,
            }
            access_token = create_access_token(identity=user_identity, fresh=True)
            refresh_token = create_refresh_token(identity=user_identity)
            headers = {"Authorization": "Bearer {}".format(access_token)}
            response = make_response(
                jsonify(
                    {
                        "success": True,
                        "message": f"Login successful, welcome {profile.get('username').title()}",
                        "profile": user_schema.dump(profile),
                    }
                ),
                200,
                headers,
            )

            return response
        return handle_not_found("")

    except NoResultFound:
        return handle_not_found("User not found")
    except Exception as e:
        print(e)
        return handle_internal_server_error(
            "something went wrong please try again later"
        )
