# Camping Site Booking Platform - Backend API

A complete Flask-based REST API for booking camping sites, similar to Airbnb but focused on outdoor stays like tents, cabins, RV spots, and eco-friendly getaways.

## Features ✨

- **User Authentication** - JWT-based registration and login
- **Campsite Management** - CRUD operations for hosts
- **Booking System** - Date validation and availability checking
- **Reviews & Ratings** - User feedback system
- **Payment Simulation** - Mock payment processing
- **Search & Filtering** - Location and price-based search

## Quick Start 🚀

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Seed the database (optional):**
```bash
python seed_data.py
```

3. **Run the application:**
```bash
python app.py
```

4. **Test the API:**
```bash
python test_api.py
```

## API Endpoints 📋

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/profile` - Get user profile (requires auth)

### Campsites
- `GET /api/campsites` - List all campsites (with search filters)
- `POST /api/campsites` - Create campsite (requires auth)
- `GET /api/campsites/<id>` - Get single campsite
- `PUT /api/campsites/<id>` - Update campsite (host only)
- `DELETE /api/campsites/<id>` - Delete campsite (host only)

### Bookings
- `GET /api/bookings` - Get user bookings (requires auth)
- `POST /api/bookings` - Create booking (requires auth)
- `GET /api/bookings/<id>` - Get booking details (requires auth)
- `PUT /api/bookings/<id>/cancel` - Cancel booking (requires auth)

### Reviews
- `POST /api/reviews` - Create review (requires auth)
- `GET /api/reviews/<campsite_id>` - Get campsite reviews
- `PUT /api/reviews/<id>` - Update review (author only)
- `DELETE /api/reviews/<id>` - Delete review (author only)

### Payment
- `POST /api/pay` - Simulate payment for booking

## Example Usage 💡

### Register a new user:
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "password123"}'
```

### Search campsites by location:
```bash
curl "http://localhost:5000/api/campsites?location=california&max_price=100"
```

### Create a booking:
```bash
curl -X POST http://localhost:5000/api/bookings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"campsite_id": 1, "start_date": "2025-10-01", "end_date": "2025-10-03"}'
```

## Project Structure 📁

```
camping-api/
├── app.py              # Main Flask application
├── models.py           # Database models (User, Campsite, Booking, Review)
├── requirements.txt    # Python dependencies
├── seed_data.py        # Database seeding script
├── test_api.py         # API testing script
├── database.db         # SQLite database (created automatically)
└── routes/            # API route modules
    ├── auth.py        # Authentication endpoints
    ├── campsites.py   # Campsite management
    ├── bookings.py    # Booking system
    └── reviews.py     # Reviews & ratings
```

## Database Schema 🗄️

### Users
- id, name, email, password_hash, created_at

### Campsites
- id, title, description, price, location, host_id, image_url, created_at

### Bookings
- id, user_id, campsite_id, start_date, end_date, status, total_price, created_at

### Reviews
- id, user_id, campsite_id, rating (1-5), comment, created_at

## Features by Week 📅

- **Week 1**: Basic Flask setup with health endpoints ✅
- **Week 2**: User authentication with JWT ✅
- **Week 3**: Campsite CRUD operations ✅
- **Week 4**: Booking system with availability checking ✅
- **Week 5**: Reviews and ratings system ✅
- **Week 6**: Admin functions (edit/delete) ✅
- **Week 7**: Payment simulation ✅
- **Week 8**: Ready for deployment ✅

## Security Features 🔒

- Password hashing with Werkzeug
- JWT token authentication
- Input validation and sanitization
- Authorization checks for protected resources
- SQL injection prevention with SQLAlchemy ORM

## Testing 🧪

The project includes comprehensive testing:
- `test_api.py` - Automated endpoint testing
- `seed_data.py` - Sample data for manual testing
- All endpoints return proper HTTP status codes
- Error handling with descriptive messages

## Deployment Ready 🌐

The application is configured for easy deployment on platforms like:
- Render
- Railway
- PythonAnywhere
- Heroku

Environment variables supported:
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Database connection string

## Next Steps 🎯

Ready for frontend integration! The API provides:
- RESTful endpoints with JSON responses
- CORS enabled for web applications
- Comprehensive error handling
- Consistent response format