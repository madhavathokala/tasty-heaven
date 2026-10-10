import re

from flask import Blueprint, request, jsonify

from models import db
from models.contact import ContactMessage

contact_bp = Blueprint("contact", __name__, url_prefix="/api")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@contact_bp.route("/contact", methods=["POST"])
def submit_contact():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    errors = []
    if not name:
        errors.append("Name is required.")
    if not email or not EMAIL_REGEX.match(email):
        errors.append("A valid email is required.")
    if not message:
        errors.append("Message cannot be empty.")

    if errors:
        return jsonify({"success": False, "message": " ".join(errors)}), 400

    entry = ContactMessage(name=name, email=email, subject=subject, message=message)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"success": True, "message": "Thank you! Your message has been received."}), 201
