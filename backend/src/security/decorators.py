from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()

            claims = get_jwt()
            role = claims.get("role")

            if role not in roles:
                return jsonify({"error": "Acesso negado"}), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper
