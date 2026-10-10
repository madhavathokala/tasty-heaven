from datetime import datetime, timezone

from models import db


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255))  # filename served from /static
    category = db.Column(db.String(50), nullable=False, default="Starters")
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image,
            "category": self.category,
            "available": self.available,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
