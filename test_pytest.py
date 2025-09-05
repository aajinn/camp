"""
Pytest test suite for the Camping API
Run with: pytest test_pytest.py
"""

import pytest
import requests
import json
from datetime import date, timedelta

BASE_URL = 'http://localhost:5000'
API_URL = f'{BASE_URL}/api'

class TestBasicEndpoints:
    """Test basic API endpoints"""
    
    def test_home_endpoint(self):
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'version' in data
        assert data['status'] == 'active'
    
    def test_hello_endpoint(self):
        response = requests.get(f'{BASE_URL}/hello')
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'features' in data
    
    def test_health_endpoint(self):
        response = requests.get(f'{BASE_URL}/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'camping-api'

class TestCampsites:
    """Test campsite endpoints"""
    
    def test_get_all_campsites(self):
        response = requests.get(f'{API_URL}/campsites')
        assert response.status_code == 200
        data = response.json()
        assert 'campsites' in data
        assert 'total' in data
        assert isinstance(data['campsites'], list)
    
    def test_search_by_location(self):
        response = requests.get(f'{API_URL}/campsites?location=california')
        assert response.status_code == 200
        data = response.json()
        assert 'campsites' in data
        # Should find California campsites
        for campsite in data['campsites']:
            assert 'california' in campsite['location'].lower()
    
    def test_filter_by_price(self):
        response = requests.get(f'{API_URL}/campsites?max_price=50')
        assert response.status_code == 200
        data = response.json()
        assert 'campsites' in data
        # All returned campsites should be <= $50
        for campsite in data['campsites']:
            assert campsite['price'] <= 50
    
    def test_get_single_campsite(self):
        response = requests.get(f'{API_URL}/campsites/1')
        assert response.status_code == 200
        data = response.json()
        assert 'campsite' in data
        campsite = data['campsite']
        assert campsite['id'] == 1
        assert 'title' in campsite
        assert 'price' in campsite

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_new_user(self):
        user_data = {
            'name': 'Test User Pytest',
            'email': 'pytest@example.com',
            'password': 'password123'
        }
        response = requests.post(f'{API_URL}/register', json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == user_data['email']
    
    def test_login_existing_user(self):
        # First register a user
        user_data = {
            'name': 'Login Test User',
            'email': 'logintest@example.com',
            'password': 'password123'
        }
        requests.post(f'{API_URL}/register', json=user_data)
        
        # Then login
        login_data = {
            'email': 'logintest@example.com',
            'password': 'password123'
        }
        response = requests.post(f'{API_URL}/login', json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'user' in data
    
    def test_invalid_login(self):
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = requests.post(f'{API_URL}/login', json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert 'error' in data

class TestReviews:
    """Test review endpoints"""
    
    def test_get_campsite_reviews(self):
        response = requests.get(f'{API_URL}/reviews/1')
        assert response.status_code == 200
        data = response.json()
        assert 'reviews' in data
        assert 'total_reviews' in data
        assert 'average_rating' in data
        assert 'rating_breakdown' in data

class TestPayment:
    """Test payment simulation"""
    
    def test_payment_for_nonexistent_booking(self):
        payment_data = {'booking_id': 99999}
        response = requests.post(f'{API_URL}/pay', json=payment_data)
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
    
    def test_payment_missing_booking_id(self):
        response = requests.post(f'{API_URL}/pay', json={})
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data