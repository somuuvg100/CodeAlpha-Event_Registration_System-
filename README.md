# Event Registration System

A RESTful API for event registration built with Django and Django REST Framework. Users can browse events, register for events, manage their registrations, and organizers can create and manage events with attendee tracking.

## 🌟 Features

### User Features
- **User Authentication**: JWT-based registration and login
- **Event Browsing**: List all events with pagination, search, and filtering
- **Event Details**: View detailed event information including available seats
- **Event Registration**: Register for events with capacity validation
- **Registration Management**: View and cancel personal registrations
- **Re-registration**: Re-register after cancellation

### Organizer Features
- **Event Creation**: Create events with title, description, location, date, and capacity
- **Event Management**: Update and delete own events
- **Attendee Tracking**: View all registrations for your events
- **Django Admin**: Full admin interface for managing events and registrations

### Security Features
- **Permission-based Access**: Users can only manage their own data
- **Staff Privileges**: Staff users have full access to all events
- **Transaction Safety**: Database transactions prevent overbooking
- **Input Validation**: Comprehensive validation for all endpoints

## 🛠 Tech Stack

- **Backend**: Django 6.1.2
- **Database**: MongoDB (via official `django-mongodb-backend` 6.1 & PyMongo)
- **API Framework**: Django REST Framework 3.18.3
- **Authentication**: djangorestframework-simplejwt 5.5.1
- **Filtering**: django-filter 26.2
- **Environment Management**: python-decouple 3.8
- **Testing**: Django Test Framework with APITestCase

## 📋 Prerequisites

- Python 3.14+
- MongoDB 6.0+ (running locally or a MongoDB Atlas URI)
- pip
- Virtual environment (venv)

## 🚀 Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Task_2
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_NAME=event_system_db
```

### 5. Run Migrations
```bash
cd event_system
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## 📊 Database Schema

### ER Diagram Description

```
User (django.contrib.auth.models.User)
├── id (PK)
├── username
├── email
└── password

Event
├── id (PK)
├── title
├── description
├── location
├── date_time
├── capacity
├── created_by (FK → User.id)
└── created_at

Registration
├── id (PK)
├── user (FK → User.id) [UNIQUE(user, event)]
├── event (FK → Event.id)
├── status (confirmed/cancelled)
└── registered_at

Relationships:
- User → Event (One-to-Many): A user can create multiple events
- Event → Registration (One-to-Many): An event can have multiple registrations
- User → Registration (One-to-Many): A user can have multiple registrations
- Registration → Event (Many-to-One): Each registration belongs to one event
```

### Constraints
- **Unique Constraint**: `(user, event)` prevents duplicate registrations
- **Foreign Keys**: Cascade delete for referential integrity
- **Capacity Validation**: Prevents overbooking via application logic

## 📡 API Documentation

### Base URL
```
http://127.0.0.1:8000/api/
```

### Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

### Auth Endpoints

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "TestPass123!",
  "password_confirm": "TestPass123!"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "testuser",
  "password": "TestPass123!"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Event Endpoints

#### List Events
```http
GET /api/events/
```

**Query Parameters:**
- `?page=2` - Page number
- `?page_size=20` - Items per page (max 100)
- `?search=Python` - Search in title and location
- `?upcoming=true` - Filter for upcoming events only

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Tech Conference 2026",
      "description": "Annual technology conference...",
      "location": "San Francisco Convention Center",
      "date_time": "2026-11-21T16:16:51.213599Z",
      "capacity": 500,
      "seats_left": 500,
      "created_by_username": "testuser",
      "created_at": "2026-10-22T16:16:51.214726Z"
    }
  ]
}
```

#### Event Details
```http
GET /api/events/{id}/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Tech Conference 2026",
  "description": "Annual technology conference...",
  "location": "San Francisco Convention Center",
  "date_time": "2026-11-21T16:16:51.213599Z",
  "capacity": 500,
  "seats_left": 500,
  "created_by_username": "testuser",
  "created_at": "2026-10-22T16:16:51.214726Z"
}
```

#### Create Event (Authenticated)
```http
POST /api/events/create/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "New Event",
  "description": "Event description",
  "location": "Event Location",
  "date_time": "2026-11-15T10:00:00Z",
  "capacity": 100
}
```

**Response (201 Created):**
```json
{
  "title": "New Event",
  "description": "Event description",
  "location": "Event Location",
  "date_time": "2026-11-15T10:00:00Z",
  "capacity": 100
}
```

#### Update Event (Creator/Staff Only)
```http
PUT /api/events/{id}/update/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Event",
  "description": "Updated description",
  "location": "Updated Location",
  "date_time": "2026-11-15T10:00:00Z",
  "capacity": 150
}
```

**Response (200 OK):**
```json
{
  "title": "Updated Event",
  "description": "Updated description",
  "location": "Updated Location",
  "date_time": "2026-11-15T10:00:00Z",
  "capacity": 150
}
```

#### Delete Event (Creator/Staff Only)
```http
DELETE /api/events/{id}/update/
Authorization: Bearer <token>
```

**Response (204 No Content)**

---

### Registration Endpoints

#### Register for Event (Authenticated)
```http
POST /api/events/{id}/register/
Authorization: Bearer <token>
```

**Response (201 Created):**
```json
{
  "detail": "Registration successful.",
  "registration": {
    "id": 1,
    "user": 1,
    "username": "testuser",
    "event": 1,
    "event_title": "Tech Conference 2026",
    "event_detail": { ... },
    "status": "confirmed",
    "registered_at": "2026-10-22T16:23:31.953749Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Event is full or in the past
- `409 Conflict`: Already registered
- `404 Not Found`: Event doesn't exist

#### View My Registrations (Authenticated)
```http
GET /api/registrations/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": 1,
    "username": "testuser",
    "event": 1,
    "event_title": "Tech Conference 2026",
    "event_detail": { ... },
    "status": "confirmed",
    "registered_at": "2026-10-22T16:23:31.953749Z"
  }
]
```

#### Cancel Registration (Authenticated)
```http
POST /api/registrations/{id}/cancel/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "detail": "Registration cancelled successfully.",
  "registration": {
    "id": 1,
    "user": 1,
    "username": "testuser",
    "event": 1,
    "event_title": "Tech Conference 2026",
    "event_detail": { ... },
    "status": "cancelled",
    "registered_at": "2026-10-22T16:23:31.953749Z"
  }
}
```

**Error Responses:**
- `403 Forbidden`: Trying to cancel someone else's registration
- `404 Not Found`: Registration doesn't exist

#### View Event Registrations (Creator/Staff Only)
```http
GET /api/events/{id}/registrations/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": 1,
    "username": "testuser",
    "event": 1,
    "event_title": "Tech Conference 2026",
    "event_detail": { ... },
    "status": "confirmed",
    "registered_at": "2026-10-22T16:23:31.953749Z"
  }
]
```

**Error Responses:**
- `403 Forbidden`: Not the event creator or staff

---

### Health Check
```http
GET /api/health/
```

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

## 🧪 Testing

### Run All Tests
```bash
cd event_system
python manage.py test events
```

### Run with Verbose Output
```bash
python manage.py test events --verbosity=2
```

### Test Coverage
See [TESTING.md](TESTING.md) for detailed testing guide.

## 🎨 Design Decisions

### Transaction Safety for Overbooking Prevention
**Decision**: Use database transactions (`transaction.atomic()`) during registration to prevent race conditions.

**Rationale**: When multiple users register simultaneously, without transactions, the capacity check and registration creation could interleave, allowing more registrations than capacity. Transactions ensure atomicity - either both operations succeed or both fail.

**Implementation**:
```python
with transaction.atomic():
    # Check capacity
    # Create registration
```

### Soft Cancel (Status Field Instead of Deletion)
**Decision**: Use a `status` field ('confirmed'/'cancelled') instead of deleting registrations.

**Rationale**:
- Preserves registration history for analytics
- Allows re-registration after cancellation
- Enables audit trails
- Simplifies reporting (total registrations vs confirmed)

**Implementation**:
```python
class Registration(models.Model):
    status = models.CharField(choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')])
```

### JWT Authentication over Token Authentication
**Decision**: Use JWT (djangorestframework-simplejwt) instead of DRF's built-in TokenAuthentication.

**Rationale**:
- Stateless - no database lookups per request
- Better for scaling
- Built-in token refresh mechanism
- Industry standard for modern APIs
- No extra database table needed

### Environment Variables with python-decouple
**Decision**: Use python-decouple for environment variable management.

**Rationale**:
- Clean separation of config from code
- Easy deployment to different environments
- Secure credential management
- Type casting support (bool, list, etc.)

## 🔮 Future Improvements

### Short Term
- [ ] Email confirmations for registrations
- [ ] Waitlist functionality for full events
- [ ] Event reminders before start time
- [ ] Event categories and tags
- [ ] Event images/media support

### Medium Term
- [ ] Payment integration (Stripe)
- [ ] Ticket generation (QR codes)
- [ ] Event ratings and reviews
- [ ] Social sharing features
- [ ] Calendar integration (ICS export)

### Long Term
- [ ] Real-time event updates (WebSockets)
- [ ] Mobile app API optimization
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Event recommendation engine

### Infrastructure
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Monitoring and logging
- [ ] Rate limiting
- [ ] API versioning

## 📁 Postman Collection Structure

Create a Postman collection with the following folders:

### 📁 Event Registration System

#### 📁 Authentication
- POST `/api/auth/register/` - Register User
- POST `/api/auth/login/` - Login

#### 📁 Events (Public)
- GET `/api/events/` - List Events
- GET `/api/events/{id}/` - Event Details
- GET `/api/health/` - Health Check

#### 📁 Events (Protected)
- POST `/api/events/create/` - Create Event
- PUT `/api/events/{id}/update/` - Update Event
- DELETE `/api/events/{id}/update/` - Delete Event
- GET `/api/events/{id}/registrations/` - View Event Registrations

#### 📁 Registrations (Protected)
- GET `/api/registrations/` - My Registrations
- POST `/api/events/{id}/register/` - Register for Event
- POST `/api/registrations/{id}/cancel/` - Cancel Registration

### Environment Variables in Postman
```
BASE_URL = http://127.0.0.1:8000/api
ACCESS_TOKEN = {{login_response.access}}
```

### Pre-request Script for Authentication
```javascript
if (pm.environment.get("ACCESS_TOKEN")) {
    pm.request.headers.add({
        key: 'Authorization',
        value: 'Bearer ' + pm.environment.get("ACCESS_TOKEN")
    });
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Django REST Framework documentation
- djangorestframework-simplejwt documentation
- python-decouple documentation
