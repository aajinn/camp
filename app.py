from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from models import db
from routes.auth import auth_bp
from routes.campsites import campsites_bp
from routes.bookings import bookings_bp
from routes.reviews import reviews_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///database.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-string")

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(campsites_bp, url_prefix="/api")
    app.register_blueprint(bookings_bp, url_prefix="/api")
    app.register_blueprint(reviews_bp, url_prefix="/api")

    @app.route("/")
    def home():
        """Welcome endpoint"""
        return jsonify(
            {
                "message": "Welcome to Camping Site Booking API",
                "version": "1.0.0",
                "status": "active",
                "endpoints": {
                    "auth": "/api/register, /api/login",
                    "campsites": "/api/campsites",
                    "bookings": "/api/bookings",
                    "reviews": "/api/reviews",
                    "payment": "/api/pay",
                },
            }
        )

    @app.route("/hello")
    def hello():
        """Simple hello endpoint"""
        return jsonify(
            {
                "message": "Hello from Camping API!",
                "features": [
                    "User Authentication",
                    "Campsite Management",
                    "Booking System",
                    "Reviews & Ratings",
                    "Payment Simulation",
                ],
            }
        )

    @app.route("/health")
    def health():
        """Health check endpoint"""
        return jsonify(
            {"status": "healthy", "service": "camping-api", "database": "connected"}
        )

    # Create tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
