"""
Simple API testing script
Run this to test all endpoints: python test_api.py
"""

import requests
import json
import sys
import time

BASE_URL = 'http://localhost:5000'
API_URL = f'{BASE_URL}/api'

def test_basic_endpoints():
    """Test basic endpoints"""
    print("Testing basic endpoints...")
    
    # Test home
    response = requests.get(BASE_URL)
    print(f"GET / - Status: {response.status_code}")
    
    # Test hello
    response = requests.get(f'{BASE_URL}/hello')
    print(f"GET /hello - Status: {response.status_code}")
    
    # Test health
    response = requests.get(f'{BASE_URL}/health')
    print(f"GET /health - Status: {response.status_code}")

def test_auth_flow():
    """Test authentication flow"""
    print("\nTesting authentication...")
    
    # Register new user
    user_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    response = requests.post(f'{API_URL}/register', json=user_data)
    print(f"POST /register - Status: {response.status_code}")
    
    if response.status_code == 201:
        token = response.json()['access_token']
        print("Registration successful, got token")
        
        # Test login
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        response = requests.post(f'{API_URL}/login', json=login_data)
        print(f"POST /login - Status: {response.status_code}")
        
        return token
    
    return None

def test_campsites(token):
    """Test campsite endpoints"""
    print("\nTesting campsites...")
    
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    # Create campsite
    if token:
        campsite_data = {
            'title': 'Test Campsite',
            'description': 'A test campsite for API testing',
            'price': 30.0,
            'location': 'Test Location',
            'image_url': 'https://example.com/test.jpg'
        }
        
        response = requests.post(f'{API_URL}/campsites', json=campsite_data, headers=headers)
        print(f"POST /campsites - Status: {response.status_code}")
        
        if response.status_code == 201:
            campsite_id = response.json()['campsite']['id']
            print(f"Created campsite with ID: {campsite_id}")
            return campsite_id
    
    # Get all campsites
    response = requests.get(f'{API_URL}/campsites')
    print(f"GET /campsites - Status: {response.status_code}")
    
    return None

def test_bookings(token, campsite_id):
    """Test booking endpoints"""
    if not token or not campsite_id:
        print("\nSkipping booking tests (need token and campsite)")
        return
    
    print("\nTesting bookings...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create booking
    from datetime import date, timedelta
    start_date = (date.today() + timedelta(days=7)).isoformat()
    end_date = (date.today() + timedelta(days=9)).isoformat()
    
    booking_data = {
        'campsite_id': campsite_id,
        'start_date': start_date,
        'end_date': end_date
    }
    
    response = requests.post(f'{API_URL}/bookings', json=booking_data, headers=headers)
    print(f"POST /bookings - Status: {response.status_code}")
    
    if response.status_code == 201:
        booking_id = response.json()['booking']['id']
        print(f"Created booking with ID: {booking_id}")
        
        # Test payment
        payment_data = {'booking_id': booking_id}
        response = requests.post(f'{API_URL}/pay', json=payment_data)
        print(f"POST /pay - Status: {response.status_code}")
        
        return booking_id
    
    return None

def test_reviews(token, campsite_id):
    """Test review endpoints"""
    if not token or not campsite_id:
        print("\nSkipping review tests (need token and campsite)")
        return
    
    print("\nTesting reviews...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get reviews for campsite
    response = requests.get(f'{API_URL}/reviews/{campsite_id}')
    print(f"GET /reviews/{campsite_id} - Status: {response.status_code}")

def wait_for_server(max_attempts=30):
    """Wait for server to be ready"""
    for i in range(max_attempts):
        try:
            response = requests.get(f'{BASE_URL}/health', timeout=2)
            if response.status_code == 200:
                print(f"Server is ready after {i+1} attempts")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False

def main():
    """Run all tests"""
    print("Starting API tests...")
    
    # Wait for server to be ready
    if not wait_for_server():
        print("Error: Server not responding after 30 seconds")
        sys.exit(1)
    
    try:
        test_basic_endpoints()
        token = test_auth_flow()
        campsite_id = test_campsites(token)
        booking_id = test_bookings(token, campsite_id)
        test_reviews(token, campsite_id)
        
        print("\n✅ All API tests completed successfully!")
        sys.exit(0)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()