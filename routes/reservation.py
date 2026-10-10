import re
from datetime import datetime

from flask import Blueprint, request, jsonify

from models import db
from models.reservation import Reservation
from routes import login_required, current_user

reservation_bp = Blueprint("reservation", __name__, url_prefix="/api")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@reservation_bp.route("/reservations", methods=["POST"])
def create_reservation():
    """
    Anyone (logged in or a guest) can submit a reservation request, but if
    they are logged in we tag the reservation with their user_id so it shows
    up under "My Reservations".
    """
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    date = (data.get("date") or "").strip()
    time = (data.get("time") or "").strip()
    guests = (data.get("guests") or "").strip()
    special_request = (data.get("special_request") or "").strip()

    errors = []
    if not name:
        errors.append("Full name is required.")
    if not email or not EMAIL_REGEX.match(email):
        errors.append("A valid email address is required.")
    if not phone or len(phone) < 7:
        errors.append("A valid phone number is required.")
    if not date:
        errors.append("Reservation date is required.")
    if not time:
        errors.append("Reservation time is required.")
    if not guests or guests.lower().startswith("select"):
        errors.append("Please select the number of guests.")
    if date:
        try:
            reservation_date = datetime.strptime(date, "%Y-%m-%d").date()

            if reservation_date < datetime.now().date():
                errors.append("Reservation date cannot be in the past.")
        except ValueError:
            errors.append("Invalid reservation date.")

    if errors:
         return jsonify({"success": False, "message": " ".join(errors)}), 400

    user = current_user()

    reservation = Reservation(
        user_id=user.id if user else None,
        name=name,
        email=email,
        phone=phone,
        reservation_date=date,
        reservation_time=time,
        guests=guests,
        special_request=special_request,
        status="pending",
    )
    db.session.add(reservation)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Table reserved successfully! We will send a confirmation shortly.",
        "reservation": reservation.to_dict(),
    }), 201


@reservation_bp.route("/my-reservations", methods=["GET"])
@login_required
def my_reservations():
    user = current_user()
    reservations = (
        Reservation.query.filter_by(user_id=user.id).order_by(Reservation.created_at.desc()).all()
    )
    return jsonify({"success": True, "reservations": [r.to_dict() for r in reservations]})
