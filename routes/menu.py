from flask import Blueprint, request, jsonify

from models import db
from models.menu import MenuItem
from routes import admin_required

menu_bp = Blueprint("menu", __name__, url_prefix="/api")


@menu_bp.route("/menu", methods=["GET"])
def get_menu():
    """Public: list all available menu items. Supports optional ?category= filter."""
    category = request.args.get("category")

    query = MenuItem.query
    if category and category.lower() != "all":
        query = query.filter(MenuItem.category.ilike(category))

    items = query.order_by(MenuItem.category, MenuItem.id).all()
    return jsonify({"success": True, "menu": [item.to_dict() for item in items]})


@menu_bp.route("/menu/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)
    if not item:
        return jsonify({"success": False, "message": "Menu item not found."}), 404
    return jsonify({"success": True, "item": item.to_dict()})


@menu_bp.route("/menu", methods=["POST"])
@admin_required
def create_menu_item():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    price = data.get("price")

    if not name:
        return jsonify({"success": False, "message": "Item name is required."}), 400

    try:
        price = float(price)
        if price <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Please provide a valid price."}), 400

    item = MenuItem(
        name=name,
        description=data.get("description", ""),
        price=price,
        image=data.get("image", ""),
        category=data.get("category", "Starters"),
        available=bool(data.get("available", True)),
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({"success": True, "message": "Menu item created.", "item": item.to_dict()}), 201


@menu_bp.route("/menu/<int:item_id>", methods=["PUT"])
@admin_required
def update_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)
    if not item:
        return jsonify({"success": False, "message": "Menu item not found."}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        item.name = (data.get("name") or "").strip() or item.name
    if "description" in data:
        item.description = data.get("description")
    if "price" in data:
        try:
            item.price = float(data.get("price"))
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Please provide a valid price."}), 400
    if "image" in data:
        item.image = data.get("image")
    if "category" in data:
        item.category = data.get("category")
    if "available" in data:
        item.available = bool(data.get("available"))

    db.session.commit()
    return jsonify({"success": True, "message": "Menu item updated.", "item": item.to_dict()})


@menu_bp.route("/menu/<int:item_id>", methods=["DELETE"])
@admin_required
def delete_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)
    if not item:
        return jsonify({"success": False, "message": "Menu item not found."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": True, "message": "Menu item deleted."})
