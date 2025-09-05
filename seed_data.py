"""
Seed script to populate the database with sample data for testing
Run this after setting up the database: python seed_data.py
"""

from app import create_app
from models import db, User, Campsite, Booking, Review
from datetime import date, timedelta


def seed_database():
    app = create_app()

    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create sample users
        users = [
            User(name="John Doe", email="john@example.com"),
            User(name="Jane Smith", email="jane@example.com"),
            User(name="Mike Johnson", email="mike@example.com"),
            User(name="Sarah Wilson", email="sarah@example.com"),
        ]

        for user in users:
            user.set_password("password123")
            db.session.add(user)

        db.session.commit()

        # Create sample campsites
        campsites = [
            Campsite(
                title="Mountain View Tent Site",
                description="Beautiful tent camping with stunning mountain views. Perfect for hikers and nature lovers.",
                price=25.0,
                location="Rocky Mountain National Park, Colorado",
                host_id=1,
                image_url="https://example.com/mountain-tent.jpg",
            ),
            Campsite(
                title="Lakeside Cabin Retreat",
                description="Cozy cabin by the lake with fishing access and kayak rentals available.",
                price=85.0,
                location="Lake Tahoe, California",
                host_id=2,
                image_url="https://example.com/lakeside-cabin.jpg",
            ),
            Campsite(
                title="Desert RV Paradise",
                description="Full hookup RV site in the beautiful Sonoran Desert with hiking trails nearby.",
                price=45.0,
                location="Phoenix, Arizona",
                host_id=1,
                image_url="https://example.com/desert-rv.jpg",
            ),
            Campsite(
                title="Forest Glamping Pod",
                description="Luxury glamping experience in the heart of the redwood forest.",
                price=120.0,
                location="Humboldt County, California",
                host_id=3,
                image_url="https://example.com/forest-pod.jpg",
            ),
            Campsite(
                title="Beach Camping Spot",
                description="Oceanfront camping with direct beach access and fire pits.",
                price=35.0,
                location="Big Sur, California",
                host_id=2,
                image_url="https://example.com/beach-camp.jpg",
            ),
        ]

        for campsite in campsites:
            db.session.add(campsite)

        db.session.commit()

        # Create sample bookings
        today = date.today()
        bookings = [
            Booking(
                user_id=3,
                campsite_id=1,
                start_date=today + timedelta(days=7),
                end_date=today + timedelta(days=10),
                total_price=75.0,
                status="paid",
            ),
            Booking(
                user_id=4,
                campsite_id=2,
                start_date=today + timedelta(days=14),
                end_date=today + timedelta(days=16),
                total_price=170.0,
                status="confirmed",
            ),
            Booking(
                user_id=3,
                campsite_id=4,
                start_date=today - timedelta(days=30),
                end_date=today - timedelta(days=28),
                total_price=240.0,
                status="paid",
            ),
        ]

        for booking in bookings:
            db.session.add(booking)

        db.session.commit()

        # Create sample reviews
        reviews = [
            Review(
                user_id=3,
                campsite_id=4,
                rating=5,
                comment="Amazing glamping experience! The pod was clean and comfortable with great forest views.",
            ),
            Review(
                user_id=4,
                campsite_id=1,
                rating=4,
                comment="Great mountain views and well-maintained site. Could use better bathroom facilities.",
            ),
        ]

        for review in reviews:
            db.session.add(review)

        db.session.commit()

        print("Database seeded successfully!")
        print(
            f"Created {len(users)} users, {len(campsites)} campsites, {len(bookings)} bookings, and {len(reviews)} reviews"
        )


if __name__ == "__main__":
    seed_database()
