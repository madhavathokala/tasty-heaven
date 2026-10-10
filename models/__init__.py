"""
models package

`db` is created here (not in app.py) so that every model file can simply do
`from models import db` without causing circular imports with app.py.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so that they are registered with SQLAlchemy's metadata
# as soon as the models package is imported (needed for db.create_all()).
from models.user import User          # noqa: E402,F401
from models.menu import MenuItem      # noqa: E402,F401
from models.reservation import Reservation  # noqa: E402,F401
from models.order import Order, OrderItem   # noqa: E402,F401
from models.contact import ContactMessage   # noqa: E402,F401
