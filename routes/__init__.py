"""
routes package

Holds shared helpers (login_required / admin_required decorators) used by
every blueprint, plus the blueprint imports needed for app.py to register
them.
"""

from functools import wraps

from flask import session, jsonify

from models import db
from models.user import User


def current_user():
    """Return the logged-in User object, or None if nobody is logged in."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"success": False, "message": "Please login first."}), 401
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"success": False, "message": "Please login first."}), 401
        if session.get("role") != "admin":
            return jsonify({"success": False, "message": "Admin access required."}), 403
        return view_func(*args, **kwargs)
    return wrapped
