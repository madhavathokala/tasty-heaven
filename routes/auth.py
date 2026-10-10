import re

from flask import Blueprint, request, jsonify, session

from models import db
from models.user import User
from routes import current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # ---- validation ----
    if not name or len(name) < 2:
        return jsonify({"success": False, "message": "Please enter a valid name."}), 400

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    if not password or len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "An account with this email already exists."}), 400

    user = User(name=name, email=email, role="user")
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Auto login after registration
    session["user_id"] = user.id
    session["role"] = user.role
    session["name"] = user.name

    return jsonify({"success": True, "message": "Account created successfully!", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    session["user_id"] = user.id
    session["role"] = user.role
    session["name"] = user.name

    return jsonify({"success": True, "message": "Login successful!", "user": user.to_dict()})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})


@auth_bp.route("/me", methods=["GET"])
def me():
    user = current_user()
    if not user:
        return jsonify({"success": False, "authenticated": False}), 200
    return jsonify({"success": True, "authenticated": True, "user": user.to_dict()})
