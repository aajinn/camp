from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Review, Campsite, Booking

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    """Create a new review for a campsite"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['campsite_id', 'rating']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'error': 'Campsite ID and rating are required'}), 400
        
        campsite_id = data['campsite_id']
        rating = data['rating']
        comment = data.get('comment', '').strip()
        
        # Validate campsite exists
        campsite = Campsite.query.get(campsite_id)
        if not campsite:
            return jsonify({'error': 'Campsite not found'}), 404
        
        # Validate rating
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid rating format'}), 400
        
        # Check if user has stayed at this campsite
        booking = Booking.query.filter_by(
            user_id=user_id,
            campsite_id=campsite_id,
            status='paid'
        ).first()
        
        if not booking:
            return jsonify({'error': 'You can only review campsites you have booked and paid for'}), 403
        
        # Check if user already reviewed this campsite
        existing_review = Review.query.filter_by(
            user_id=user_id,
            campsite_id=campsite_id
        ).first()
        
        if existing_review:
            return jsonify({'error': 'You have already reviewed this campsite'}), 400
        
        # Create review
        review = Review(
            user_id=user_id,
            campsite_id=campsite_id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review created successfully',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create review'}), 500

@reviews_bp.route('/reviews/<int:campsite_id>', methods=['GET'])
def get_campsite_reviews(campsite_id):
    """Get all reviews for a specific campsite"""
    try:
        # Validate campsite exists
        campsite = Campsite.query.get(campsite_id)
        if not campsite:
            return jsonify({'error': 'Campsite not found'}), 404
        
        reviews = Review.query.filter_by(campsite_id=campsite_id).order_by(Review.created_at.desc()).all()
        
        # Calculate rating statistics
        if reviews:
            ratings = [review.rating for review in reviews]
            avg_rating = sum(ratings) / len(ratings)
            rating_counts = {i: ratings.count(i) for i in range(1, 6)}
        else:
            avg_rating = 0
            rating_counts = {i: 0 for i in range(1, 6)}
        
        return jsonify({
            'reviews': [review.to_dict() for review in reviews],
            'total_reviews': len(reviews),
            'average_rating': round(avg_rating, 1),
            'rating_breakdown': rating_counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get reviews'}), 500

@reviews_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """Update a review (author only)"""
    try:
        user_id = get_jwt_identity()
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        # Check if user is the author
        if review.user_id != user_id:
            return jsonify({'error': 'Only the review author can update this review'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update rating if provided
        if 'rating' in data:
            try:
                rating = int(data['rating'])
                if rating < 1 or rating > 5:
                    return jsonify({'error': 'Rating must be between 1 and 5'}), 400
                review.rating = rating
            except ValueError:
                return jsonify({'error': 'Invalid rating format'}), 400
        
        # Update comment if provided
        if 'comment' in data:
            review.comment = data['comment'].strip()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review updated successfully',
            'review': review.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update review'}), 500

@reviews_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete a review (author only)"""
    try:
        user_id = get_jwt_identity()
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        # Check if user is the author
        if review.user_id != user_id:
            return jsonify({'error': 'Only the review author can delete this review'}), 403
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete review'}), 500