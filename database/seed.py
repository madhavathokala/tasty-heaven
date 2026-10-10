"""
Seed script for Tasty Heaven.

Run with:
    python database/seed.py

This will:
  1. Create all database tables (if they don't already exist).
  2. Create a sample ADMIN account.
  3. Create a sample USER account.
  4. Populate the menu with the exact dishes/prices/images that existed in
     the original Tasty Heaven frontend (menu.html).

Safe to re-run: it checks for existing rows before inserting so you will
not get duplicate accounts or menu items.
"""

import os
import sys

# Make sure the project root is importable when this script is run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app          # noqa: E402
from models import db               # noqa: E402
from models.user import User        # noqa: E402
from models.menu import MenuItem    # noqa: E402

# ---------------------------------------------------------------------------
# Menu data — taken directly from the original menu.html cards
# (name, description, price, image filename, category)
# ---------------------------------------------------------------------------
MENU_ITEMS = [
    ("Chicken Dum Biryani", "Hyderabadi dum biryani served with raita and salan.",
     299, "image 1.jpg", "Non Veg"),
    ("Mutton Biryani", "Tender mutton cooked with aromatic basmati rice.",
     399, "image 2.avif", "Non Veg"),
    ("Paneer Butter Masala", "Creamy tomato gravy with soft paneer cubes.",
     240, "image 3.jpg", "Veg"),
    ("Chicken 65", "Crispy spicy chicken starter.",
     220, "image 4.jpg", "Starters"),
    ("Butter Naan", "Fresh tandoor naan topped with butter.",
     45, "image 5.jpg", "Veg"),
    ("Veg Fried Rice", "Chinese style fried rice with vegetables.",
     180, "image 6.jpg", "Veg"),
    ("Chilli Chicken", "Spicy Indo-Chinese chicken recipe.",
     260, "image 7.jpg", "Starters"),
    ("Farm Fresh Pizza", "Loaded with vegetables and mozzarella cheese.",
     349, "image 8.webp", "Veg"),
    ("Gulab Jamun", "Soft milk dumplings served hot.",
     120, "gulab jam.jpg", "Desserts"),
    ("Brownie Ice Cream", "Chocolate brownie served with vanilla ice cream.",
     180, "brownie-ice-cream.jpg", "Desserts"),
    ("Ice Cream", "Chocolate, Vanilla & Strawberry flavors.",
     90, "ice-cream.jpg", "Desserts"),
    ("Mango Lassi", "Fresh mango yogurt drink.",
     99, "Mango-Lassi.jpg", "Drinks"),
    ("Fresh Lime Soda", "Sweet & Salt refreshing drink.",
     70, "LimeSoda.webp", "Drinks"),
    ("Cold Coffee", "Creamy cold coffee topped with ice cream.",
     140, "cold coffee.jpg", "Drinks"),
]


def seed():
    app = create_app()

    with app.app_context():
        db.create_all()
        print("[OK] Database tables created (or already existed).")

        # ---------------- Admin account ----------------
        admin_email = "admin@tastyheaven.com"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(name="Admin", email=admin_email, role="admin")
            admin.set_password("Admin@123")
            db.session.add(admin)
            print(f"[OK] Created admin account -> {admin_email} / Admin@123")
        else:
            print(f"[SKIP] Admin account already exists -> {admin_email}")

        # ---------------- Sample user account ----------------
        user_email = "user@tastyheaven.com"
        sample_user = User.query.filter_by(email=user_email).first()
        if not sample_user:
            sample_user = User(name="Test User", email=user_email, role="user")
            sample_user.set_password("User@123")
            db.session.add(sample_user)
            print(f"[OK] Created sample user account -> {user_email} / User@123")
        else:
            print(f"[SKIP] Sample user account already exists -> {user_email}")

        db.session.commit()

        # ---------------- Menu items ----------------
        created_count = 0
        for name, description, price, image, category in MENU_ITEMS:
            existing = MenuItem.query.filter_by(name=name).first()
            if existing:
                continue
            item = MenuItem(
                name=name,
                description=description,
                price=price,
                image=image,
                category=category,
                available=True,
            )
            db.session.add(item)
            created_count += 1

        db.session.commit()
        print(f"[OK] Menu seeding complete. {created_count} new item(s) added "
              f"({MenuItem.query.count()} total in database).")

        print("\nSeed complete! You can now run the app with: python app.py")


if __name__ == "__main__":
    seed()
