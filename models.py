from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    campsites = db.relationship("Campsite", backref="host", lazy=True)
    bookings = db.relationship("Booking", backref="user", lazy=True)
    reviews = db.relationship("Review", backref="user", lazy=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }


class Campsite(db.Model):
    """Campsite model for listings"""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", backref="campsite", lazy=True)
    reviews = db.relationship("Review", backref="campsite", lazy=True)

    def get_average_rating(self):
        """Calculate average rating from reviews"""
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "location": self.location,
            "host_id": self.host_id,
            "host_name": self.host.name,
            "image_url": self.image_url,
            "average_rating": round(self.get_average_rating(), 1),
            "review_count": len(self.reviews),
            "created_at": self.created_at.isoformat(),
        }


class Booking(db.Model):
    """Booking model for reservations"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    campsite_id = db.Column(db.Integer, db.ForeignKey("campsite.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, confirmed, paid, cancelled
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "campsite_id": self.campsite_id,
            "campsite_title": self.campsite.title,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status,
            "total_price": self.total_price,
            "created_at": self.created_at.isoformat(),
        }


class Review(db.Model):
    """Review model for campsite feedback"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    campsite_id = db.Column(db.Integer, db.ForeignKey("campsite.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "campsite_id": self.campsite_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }
