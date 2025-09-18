from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role or "").lower() != "admin":
            return abort(403)
        return fn(*args, **kwargs)
    return wrapper

