import os

from flask import Flask, render_template, session, jsonify, request

from config import Config
from models import db
from models.user import User


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="",   # serve static/* directly at the site root, e.g. static/style.css -> /style.css
        template_folder="templates",
    )
    app.config.from_object(Config)

    # Make sure the instance/ folder (holds the SQLite file) exists
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)

    # ---------------- Register API blueprints ----------------
    from routes.auth import auth_bp
    from routes.menu import menu_bp
    from routes.reservation import reservation_bp
    from routes.order import order_bp
    from routes.contact import contact_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)

    # ---------------- Make current user available in every template ----------------
    @app.context_processor
    def inject_user():
        user = None
        user_id = session.get("user_id")
        if user_id:
            user = db.session.get(User, user_id)
        return {"current_user": user}

    # ---------------- Page routes (serve the existing frontend HTML) ----------------
    # Kept as plain "*.html" routes (matching the original relative links in
    # the frontend) so that no <a href="..."> in the existing HTML had to be
    # rewritten.

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/index.html")
    def index_page():
        return render_template("index.html")

    @app.route("/about.html")
    def about_page():
        return render_template("about.html")

    @app.route("/menu.html")
    def menu_page():
        return render_template("menu.html")

    @app.route("/gallery.html")
    def gallery_page():
        return render_template("gallery.html")

    @app.route("/reservation.html")
    def reservation_page():
        return render_template("reservation.html")

    @app.route("/contact.html")
    def contact_page():
        return render_template("contact.html")

    @app.route("/login.html")
    def login_page():
        return render_template("login.html")

    @app.route("/signup.html")
    def signup_page():
        return render_template("signup.html")

    @app.route("/cart.html")
    def cart_page():
        return render_template("cart.html")

    @app.route("/orders.html")
    def orders_page():
        return render_template("orders.html")

    @app.route("/my-reservations.html")
    def my_reservations_page():
        return render_template("my-reservations.html")

    @app.route("/admin.html")
    def admin_page():
        return render_template("admin.html")

    # ---------------- Error handlers ----------------
    def wants_json():
        return request.path.startswith("/api") or request.accept_mimetypes["application/json"] >= \
            request.accept_mimetypes["text/html"]

    @app.errorhandler(400)
    def bad_request(e):
        if wants_json():
            return jsonify({"success": False, "message": "Bad request."}), 400
        return render_template("index.html"), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if wants_json():
            return jsonify({"success": False, "message": "Please login first."}), 401
        return render_template("login.html"), 401

    @app.errorhandler(403)
    def forbidden(e):
        if wants_json():
            return jsonify({"success": False, "message": "You do not have permission to do that."}), 403
        return render_template("index.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        if wants_json():
            return jsonify({"success": False, "message": "Resource not found."}), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        if wants_json():
            return jsonify({"success": False, "message": "Something went wrong on our end. Please try again."}), 500
        return render_template("index.html"), 500
    with app.app_context():
        db.create_all()
        with app.app_context():
    db.create_all()

    admin_email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "")

    if admin_email and admin_password:
        admin = User.query.filter_by(email=admin_email).first()

        if not admin:
            admin = User(
                name="Admin",
                email=admin_email,
                role="admin"
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()

   return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ensure tables exist even if seed.py was never run
    app.run(debug=True)
