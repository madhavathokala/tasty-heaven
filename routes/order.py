from flask import Blueprint, request, jsonify

from models import db
from models.menu import MenuItem
from models.order import Order, OrderItem
from routes import login_required, current_user

order_bp = Blueprint("order", __name__, url_prefix="/api")

DELIVERY_FEE = 40.0


@order_bp.route("/orders", methods=["POST"])
@login_required
def create_order():
    """
    Body: { "items": [ { "menu_item_id": 1, "quantity": 2 }, ... ] }

    IMPORTANT: the price is NEVER taken from the request. We look up each
    menu_item_id in the database and use the price stored there. The total
    is calculated entirely on the server.
    """
    data = request.get_json(silent=True) or {}
    cart_items = data.get("items") or []

    if not cart_items or not isinstance(cart_items, list):
        return jsonify({"success": False, "message": "Your cart is empty."}), 400

    user = current_user()

    order_items = []
    total = 0.0

    for entry in cart_items:
        try:
            menu_item_id = int(entry.get("menu_item_id"))
            quantity = int(entry.get("quantity", 1))
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Invalid item in cart."}), 400

        if quantity < 1:
            return jsonify({"success": False, "message": "Quantity must be at least 1."}), 400

        menu_item = db.session.get(MenuItem, menu_item_id)
        if not menu_item or not menu_item.available:
            return jsonify({
                "success": False,
                "message": f"Menu item #{menu_item_id} is not available."
            }), 400

        # Price comes from the DATABASE, never trusted from the client.
        line_total = menu_item.price * quantity
        total += line_total

        order_items.append(OrderItem(
            menu_item_id=menu_item.id,
            quantity=quantity,
            price=menu_item.price,
        ))

    total += DELIVERY_FEE

    order = Order(user_id=user.id, total_amount=round(total, 2), status="placed")
    order.items = order_items

    db.session.add(order)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Order placed successfully!",
        "order": order.to_dict(),
    }), 201


@order_bp.route("/orders", methods=["GET"])
@login_required
def get_my_orders():
    user = current_user()
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return jsonify({"success": True, "orders": [o.to_dict() for o in orders]})


@order_bp.route("/orders/<int:order_id>", methods=["GET"])
@login_required
def get_order(order_id):
    user = current_user()
    order = db.session.get(Order, order_id)

    if not order or (order.user_id != user.id and user.role != "admin"):
        return jsonify({"success": False, "message": "Order not found."}), 404

    return jsonify({"success": True, "order": order.to_dict()})
