from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Campsite, User
from sqlalchemy import or_

campsites_bp = Blueprint("campsites", __name__)


@campsites_bp.route("/campsites", methods=["POST"])
@jwt_required()
def create_campsite():
    """Create a new campsite (host only)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        required_fields = ["title", "description", "price", "location"]
        if not data or not all(k in data for k in required_fields):
            return (
                jsonify(
                    {"error": "Title, description, price, and location are required"}
                ),
                400,
            )

        # Validate data types
        try:
            price = float(data["price"])
            if price <= 0:
                return jsonify({"error": "Price must be greater than 0"}), 400
        except ValueError:
            return jsonify({"error": "Invalid price format"}), 400

        # Create campsite
        campsite = Campsite(
            title=data["title"].strip(),
            description=data["description"].strip(),
            price=price,
            location=data["location"].strip(),
            host_id=user_id,
            image_url=data.get("image_url", "").strip(),
        )

        db.session.add(campsite)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Campsite created successfully",
                    "campsite": campsite.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create campsite"}), 500


@campsites_bp.route("/campsites", methods=["GET"])
def get_campsites():
    """Get all campsites with optional search filters"""
    try:
        # Get query parameters
        location = request.args.get("location", "").strip()
        max_price = request.args.get("max_price")
        min_price = request.args.get("min_price")

        # Start with base query
        query = Campsite.query

        # Apply filters
        if location:
            query = query.filter(Campsite.location.ilike(f"%{location}%"))

        if min_price:
            try:
                min_price = float(min_price)
                query = query.filter(Campsite.price >= min_price)
            except ValueError:
                return jsonify({"error": "Invalid min_price format"}), 400

        if max_price:
            try:
                max_price = float(max_price)
                query = query.filter(Campsite.price <= max_price)
            except ValueError:
                return jsonify({"error": "Invalid max_price format"}), 400

        # Execute query
        campsites = query.all()

        return (
            jsonify(
                {
                    "campsites": [campsite.to_dict() for campsite in campsites],
                    "total": len(campsites),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Failed to get campsites"}), 500


@campsites_bp.route("/campsites/<int:campsite_id>", methods=["GET"])
def get_campsite(campsite_id):
    """Get single campsite details"""
    try:
        campsite = Campsite.query.get(campsite_id)

        if not campsite:
            return jsonify({"error": "Campsite not found"}), 404

        return jsonify({"campsite": campsite.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to get campsite"}), 500


@campsites_bp.route("/campsites/<int:campsite_id>", methods=["PUT"])
@jwt_required()
def update_campsite(campsite_id):
    """Update campsite (host only)"""
    try:
        user_id = get_jwt_identity()
        campsite = Campsite.query.get(campsite_id)

        if not campsite:
            return jsonify({"error": "Campsite not found"}), 404

        # Check if user is the host
        if campsite.host_id != user_id:
            return jsonify({"error": "Only the host can update this campsite"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update fields if provided
        if "title" in data:
            campsite.title = data["title"].strip()
        if "description" in data:
            campsite.description = data["description"].strip()
        if "price" in data:
            try:
                price = float(data["price"])
                if price <= 0:
                    return jsonify({"error": "Price must be greater than 0"}), 400
                campsite.price = price
            except ValueError:
                return jsonify({"error": "Invalid price format"}), 400
        if "location" in data:
            campsite.location = data["location"].strip()
        if "image_url" in data:
            campsite.image_url = data["image_url"].strip()

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Campsite updated successfully",
                    "campsite": campsite.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update campsite"}), 500


@campsites_bp.route("/campsites/<int:campsite_id>", methods=["DELETE"])
@jwt_required()
def delete_campsite(campsite_id):
    """Delete campsite (host only)"""
    try:
        user_id = get_jwt_identity()
        campsite = Campsite.query.get(campsite_id)

        if not campsite:
            return jsonify({"error": "Campsite not found"}), 404

        # Check if user is the host
        if campsite.host_id != user_id:
            return jsonify({"error": "Only the host can delete this campsite"}), 403

        db.session.delete(campsite)
        db.session.commit()

        return jsonify({"message": "Campsite deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete campsite"}), 500
