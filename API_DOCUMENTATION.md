# API Documentation - Annadan Platform

## Base URL
```
http://localhost:5000/api
```

## Authentication
All endpoints (except /auth/register, /auth/login) require JWT token in header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### 1. Register User
**POST** `/auth/register`

Request body:
```json
{
  "email": "user@example.com",
  "phone": "+91-9876543210",
  "password": "SecurePass123",
  "name": "John Doe",
  "user_type": "donor",
  "address": "123 Street Name",
  "city": "New Delhi",
  "state": "Delhi",
  "organization_name": "Optional for NGO"
}
```

Response (201):
```json
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

---

### 2. Login
**POST** `/auth/login`

Request body:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

Response (200):
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe",
    "user_type": "donor"
  }
}
```

---

## Donor Endpoints

### 1. Post Food Donation
**POST** `/donors/post-food`

Headers: `Authorization: Bearer <token>`

Request body:
```json
{
  "food_type": "Biryani",
  "quantity": 25,
  "unit": "plates",
  "description": "Fresh catered biryani from wedding",
  "pickup_time": "2024-01-15T18:00:00",
  "expiry_time": "2024-01-15T22:00:00",
  "address": "Taj Hotel, MG Road",
  "city": "New Delhi",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "donor_name": "John Doe",
  "donor_phone": "+91-9876543210"
}
```

Response (201):
```json
{
  "message": "Food posted successfully",
  "donation_id": "507f1f77bcf86cd799439012"
}
```

---

### 2. Get My Donations
**GET** `/donors/my-donations`

Headers: `Authorization: Bearer <token>`

Query parameters (optional):
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 10)

Response (200):
```json
{
  "donations": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "food_type": "Biryani",
      "quantity": 25,
      "unit": "plates",
      "status": "available",
      "location": {
        "address": "Taj Hotel, MG Road",
        "city": "New Delhi",
        "coordinates": [77.2090, 28.6139]
      },
      "created_at": "2024-01-15T17:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 3. Get Donation Details
**GET** `/donors/donation/<donation_id>`

Response (200):
```json
{
  "_id": "507f1f77bcf86cd799439012",
  "donor_id": "507f1f77bcf86cd799439011",
  "food_type": "Biryani",
  "quantity": 25,
  "unit": "plates",
  "description": "Fresh catered biryani from wedding",
  "status": "available",
  "location": {
    "address": "Taj Hotel, MG Road",
    "city": "New Delhi",
    "coordinates": [77.2090, 28.6139]
  },
  "donor_name": "John Doe",
  "donor_phone": "+91-9876543210",
  "pickup_time": "2024-01-15T18:00:00Z",
  "created_at": "2024-01-15T17:00:00Z"
}
```

---

### 4. Update Donation
**PUT** `/donors/donation/<donation_id>`

Headers: `Authorization: Bearer <token>`

Request body (send fields to update):
```json
{
  "quantity": 30,
  "description": "Updated description"
}
```

Response (200):
```json
{
  "message": "Donation updated successfully"
}
```

---

### 5. Cancel Donation
**POST** `/donors/donation/<donation_id>/cancel`

Headers: `Authorization: Bearer <token>`

Response (200):
```json
{
  "message": "Donation cancelled successfully"
}
```

---

## NGO Endpoints

### 1. Find Nearby Food
**GET** `/ngos/nearby-food`

Headers: `Authorization: Bearer <token>`

Query parameters (optional):
- `radius`: Search radius in km (default: 10)

Response (200):
```json
{
  "nearby_food": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "donor_id": "507f1f77bcf86cd799439011",
      "food_type": "Biryani",
      "quantity": 25,
      "unit": "plates",
      "location": {
        "address": "Taj Hotel, MG Road",
        "city": "New Delhi",
        "coordinates": [77.2090, 28.6139]
      },
      "distance": 2.5,
      "pickup_time": "2024-01-15T18:00:00Z"
    }
  ],
  "total": 1,
  "ngo_location": {
    "latitude": 28.6200,
    "longitude": 77.2150
  }
}
```

---

### 2. Accept Donation
**POST** `/ngos/donation/<donation_id>/accept`

Headers: `Authorization: Bearer <token>`

Response (200):
```json
{
  "message": "Donation accepted successfully",
  "donation_id": "507f1f77bcf86cd799439012"
}
```

---

### 3. Get My Collections
**GET** `/ngos/my-collections`

Headers: `Authorization: Bearer <token>`

Response (200):
```json
{
  "collections": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "food_type": "Biryani",
      "quantity": 25,
      "unit": "plates",
      "status": "accepted",
      "donor_name": "John Doe",
      "location": {
        "address": "Taj Hotel, MG Road"
      },
      "accepted_at": "2024-01-15T17:30:00Z"
    }
  ],
  "total": 1
}
```

---

### 4. Mark as Collected
**POST** `/ngos/donation/<donation_id>/collected`

Headers: `Authorization: Bearer <token>`

Response (200):
```json
{
  "message": "Marked as collected"
}
```

---

### 5. Get NGO Profile
**GET** `/ngos/profile`

Headers: `Authorization: Bearer <token>`

Response (200):
```json
{
  "_id": "507f1f77bcf86cd799439020",
  "user_id": "507f1f77bcf86cd799439011",
  "name": "Care Foundation",
  "organization_name": "Care Foundation",
  "phone": "+91-9876543210",
  "email": "care@example.com",
  "location": {
    "address": "456 Relief Street",
    "city": "New Delhi",
    "coordinates": [77.2150, 28.6200]
  },
  "verified": true,
  "total_pickups": 45,
  "rating": 4.8,
  "created_at": "2024-01-10T10:00:00Z"
}
```

---

### 6. Update NGO Profile
**PUT** `/ngos/profile`

Headers: `Authorization: Bearer <token>`

Request body:
```json
{
  "phone": "+91-9876543210",
  "address": "New Address"
}
```

Response (200):
```json
{
  "message": "Profile updated successfully"
}
```

---

## Feedback Endpoints

### 1. Submit Feedback
**POST** `/feedback/submit`

Headers: `Authorization: Bearer <token>`

Request body:
```json
{
  "donation_id": "507f1f77bcf86cd799439012",
  "rating": 5,
  "comment": "Excellent service and fresh food",
  "food_quality": "Excellent",
  "punctuality": "On time",
  "communication": "Very responsive"
}
```

Response (201):
```json
{
  "message": "Feedback submitted successfully",
  "feedback_id": "507f1f77bcf86cd799439030"
}
```

---

### 2. Get User Feedback
**GET** `/feedback/user/<user_id>`

Response (200):
```json
{
  "rating_summary": {
    "average_rating": 4.8,
    "total_reviews": 25,
    "rating_breakdown": {
      "1": 0,
      "2": 1,
      "3": 1,
      "4": 5,
      "5": 18
    }
  },
  "feedback": [
    {
      "_id": "507f1f77bcf86cd799439030",
      "donation_id": "507f1f77bcf86cd799439012",
      "from_user_id": "507f1f77bcf86cd799439011",
      "rating": 5,
      "comment": "Excellent service",
      "created_at": "2024-01-15T19:00:00Z"
    }
  ]
}
```

---

### 3. Get Leaderboard
**GET** `/feedback/leaderboard`

Response (200):
```json
{
  "leaderboard": [
    {
      "_id": "507f1f77bcf86cd799439020",
      "name": "Care Foundation",
      "organization_name": "Care Foundation",
      "total_pickups": 45,
      "average_rating": 4.9,
      "total_reviews": 25
    }
  ]
}
```

---

## Admin Endpoints

### 1. Get Dashboard
**GET** `/admin/dashboard`

Headers: `Authorization: Bearer <token>`

Response (200):
```json
{
  "donations": {
    "total_donations": 150,
    "available": 45,
    "accepted": 50,
    "completed": 55
  },
  "total_users": 200,
  "total_ngos": 25,
  "verified_ngos": 20,
  "pending_ngos": 5
}
```

---

### 2. Get All Users
**GET** `/admin/users`

Headers: `Authorization: Bearer <token>`

Query parameters (optional):
- `type`: Filter by user type (donor/ngo)
- `skip`: Skip records (default: 0)
- `limit`: Limit records (default: 10)

Response (200):
```json
{
  "users": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "email": "john@example.com",
      "phone": "+91-9876543210",
      "name": "John Doe",
      "user_type": "donor",
      "is_active": true,
      "created_at": "2024-01-15T17:00:00Z"
    }
  ],
  "total": 200
}
```

---

### 3. Verify NGO
**POST** `/admin/ngos/verify/<ngo_user_id>`

Headers: `Authorization: Bearer <token>`

Response (200):
```json
{
  "message": "NGO verified successfully"
}
```

---

### 4. Get Analytics
**GET** `/admin/donations/analytics`

Response (200):
```json
{
  "stats": {
    "total_donations": 150,
    "available": 45,
    "accepted": 50,
    "completed": 55
  },
  "total_quantity_saved": 5250.5,
  "average_donation_quantity": 35,
  "most_common_food_type": "Biryani"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input format"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid token or token expired"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting
- No rate limiting currently implemented (add Redis for production)
- Recommended: 100 requests per minute per IP

## Versioning
- Current API Version: v1
- Future: `/api/v2`, `/api/v3` etc.

---

Last Updated: January 2024
