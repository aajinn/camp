from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Booking, Campsite, User
from datetime import datetime, date
import random

bookings_bp = Blueprint('bookings', __name__)

def check_availability(campsite_id, start_date, end_date, exclude_booking_id=None):
    """Check if campsite is available for given dates"""
    query = Booking.query.filter(
        Booking.campsite_id == campsite_id,
        Booking.status.in_(['confirmed', 'paid']),
        Booking.start_date < end_date,
        Booking.end_date > start_date
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    return query.first() is None

@bookings_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['campsite_id', 'start_date', 'end_date']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'error': 'Campsite ID, start date, and end date are required'}), 400
        
        # Validate campsite exists
        campsite = Campsite.query.get(data['campsite_id'])
        if not campsite:
            return jsonify({'error': 'Campsite not found'}), 404
        
        # Parse dates
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate dates
        if start_date >= end_date:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        if start_date < date.today():
            return jsonify({'error': 'Start date cannot be in the past'}), 400
        
        # Check availability
        if not check_availability(campsite.id, start_date, end_date):
            return jsonify({'error': 'Campsite is not available for selected dates'}), 400
        
        # Calculate total price
        nights = (end_date - start_date).days
        total_price = nights * campsite.price
        
        # Create booking
        booking = Booking(
            user_id=user_id,
            campsite_id=campsite.id,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='confirmed'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create booking'}), 500

@bookings_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    """Get all bookings for current user"""
    try:
        user_id = get_jwt_identity()
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings],
            'total': len(bookings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get bookings'}), 500

@bookings_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get specific booking details"""
    try:
        user_id = get_jwt_identity()
        booking = Booking.query.get(booking_id)
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check if user owns this booking or is the campsite host
        if booking.user_id != user_id and booking.campsite.host_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get booking'}), 500

@bookings_bp.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        user_id = get_jwt_identity()
        booking = Booking.query.get(booking_id)
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check if user owns this booking
        if booking.user_id != user_id:
            return jsonify({'error': 'Only the booking owner can cancel'}), 403
        
        # Check if booking can be cancelled
        if booking.status == 'cancelled':
            return jsonify({'error': 'Booking is already cancelled'}), 400
        
        if booking.start_date <= date.today():
            return jsonify({'error': 'Cannot cancel booking that has already started'}), 400
        
        booking.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel booking'}), 500

@bookings_bp.route('/pay', methods=['POST'])
def simulate_payment():
    """Simulate payment for a booking"""
    try:
        data = request.get_json()
        
        if not data or 'booking_id' not in data:
            return jsonify({'error': 'Booking ID is required'}), 400
        
        booking = Booking.query.get(data['booking_id'])
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking.status == 'paid':
            return jsonify({'error': 'Booking is already paid'}), 400
        
        if booking.status == 'cancelled':
            return jsonify({'error': 'Cannot pay for cancelled booking'}), 400
        
        # Simulate payment processing
        payment_success = random.choice([True, True, True, False])  # 75% success rate
        
        if payment_success:
            booking.status = 'paid'
            db.session.commit()
            
            print(f"Payment of ${booking.total_price} successful for booking #{booking.id}")
            
            return jsonify({
                'message': f'Payment of ${booking.total_price} successful for booking #{booking.id}',
                'booking': booking.to_dict(),
                'payment_status': 'success'
            }), 200
        else:
            return jsonify({
                'error': 'Payment failed. Please try again.',
                'payment_status': 'failed'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payment processing failed'}), 500