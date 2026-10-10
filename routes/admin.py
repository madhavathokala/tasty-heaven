from flask import Blueprint, request, jsonify

from models import db
from models.user import User
from models.reservation import Reservation
from models.order import Order
from models.contact import ContactMessage
from routes import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

VALID_RESERVATION_STATUSES = {"pending", "confirmed", "cancelled"}
VALID_ORDER_STATUSES = {"placed", "preparing", "out-for-delivery", "delivered", "cancelled"}


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"success": True, "users": [u.to_dict() for u in users]})


@admin_bp.route("/reservations", methods=["GET"])
@admin_required
def list_reservations():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return jsonify({"success": True, "reservations": [r.to_dict() for r in reservations]})


@admin_bp.route("/reservations/<int:reservation_id>", methods=["PUT"])
@admin_required
def update_reservation_status(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)
    if not reservation:
        return jsonify({"success": False, "message": "Reservation not found."}), 404

    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip().lower()

    if status not in VALID_RESERVATION_STATUSES:
        return jsonify({
            "success": False,
            "message": f"Status must be one of: {', '.join(VALID_RESERVATION_STATUSES)}"
        }), 400

    reservation.status = status
    db.session.commit()

    return jsonify({"success": True, "message": "Reservation status updated.", "reservation": reservation.to_dict()})


@admin_bp.route("/orders", methods=["GET"])
@admin_required
def list_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify({"success": True, "orders": [o.to_dict() for o in orders]})


@admin_bp.route("/orders/<int:order_id>", methods=["PUT"])
@admin_required
def update_order_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"success": False, "message": "Order not found."}), 404

    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip().lower()

    if status not in VALID_ORDER_STATUSES:
        return jsonify({
            "success": False,
            "message": f"Status must be one of: {', '.join(VALID_ORDER_STATUSES)}"
        }), 400

    order.status = status
    db.session.commit()

    return jsonify({"success": True, "message": "Order status updated.", "order": order.to_dict()})


@admin_bp.route("/contact-messages", methods=["GET"])
@admin_required
def list_contact_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify({"success": True, "messages": [m.to_dict() for m in messages]})


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def admin_stats():
    return jsonify({
        "success": True,
        "stats": {
            "total_users": User.query.filter_by(role="user").count(),
            "total_orders": Order.query.count(),
            "total_reservations": Reservation.query.count(),
            "pending_reservations": Reservation.query.filter_by(status="pending").count(),
            "total_revenue": round(
                sum(o.total_amount for o in Order.query.filter(Order.status != "cancelled").all()), 2
            ),
        }
    })
