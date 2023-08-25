from flask_jwt_extended import get_jwt_identity, jwt_required
import shortuuid
from functools import wraps
from errors import handle_forbidden


def gen_short_id():
    return shortuuid.uuid()


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user_role = current_user.get("role")
            if user_role != role:
                return handle_forbidden("")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
