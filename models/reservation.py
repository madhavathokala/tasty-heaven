from datetime import datetime, timezone

from models import db


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    reservation_date = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD
    reservation_time = db.Column(db.String(20), nullable=False)  # HH:MM
    guests = db.Column(db.String(20), nullable=False)
    special_request = db.Column(db.String(500))
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending/confirmed/cancelled
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "reservation_date": self.reservation_date,
            "reservation_time": self.reservation_time,
            "guests": self.guests,
            "special_request": self.special_request,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
