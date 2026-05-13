# 🍽️ Annadan - A Umeed
## Food Redistribution Platform for NGOs

A comprehensive web platform connecting food donors (wedding halls, parties, hotels, restaurants) with NGOs/volunteers to reduce food wastage and fight hunger.

### 🎯 Project Overview

**Annadan - A Umeed** (Hindi: "Hope - A Promise") is a full-stack web application that:
- Allows donors to post available food with location and pickup time
- Enables NGOs to discover nearby food donations in real-time
- Provides a feedback and rating system for transparency
- Tracks food saved and monitors wastage reduction
- Uses location-based matching to connect nearest donors and NGOs

### ✨ Core Features

#### 👥 User Roles

**Donors (Individuals, Hotels, Wedding Halls, Restaurants)**
- Register/login with email and phone
- Post available food with details (type, quantity, pickup time, location)
- Get notifications when NGOs accept requests
- Track donation history and impact
- Receive ratings from NGOs
- Cancel donations if needed

**NGOs (Non-Governmental Organizations)**
- Register/login and get verified by admin
- Browse available food nearby (location-based search)
- Accept donations and arrange pickups
- Track collection status and history
- Provide feedback on food quality and quantity
- Build reputation through ratings and reviews
- View leaderboard of top-performing NGOs

**Admin**
- Manage users (donors, NGOs)
- Verify NGO profiles
- View analytics dashboard (food saved, NGOs helped, donations per month)
- Monitor system health

#### 📍 Location & Tracking
- Google Maps API integration for location display
- Geolocation-based matching (finds nearest NGOs for donors)
- Distance calculation between donors and NGOs
- Customizable search radius

#### ⭐ Feedback & Rating System
- Donors rate NGOs (1-5 stars) on punctuality, food handling, communication
- NGOs rate donors on food quality, quantity, and honesty
- Average ratings and review breakdown displayed on profiles
- Leaderboard showing top-rated NGOs

#### 🔔 Notifications
- Email notifications for account events
- SMS alerts via Twilio (optional)
- Real-time notifications when donations posted nearby
- Pickup confirmation messages

### 🛠️ Tech Stack

**Frontend**
- React.js 18.2 - Modern UI framework
- React Router v6 - Client-side routing
- Bootstrap 5 + React Bootstrap - Responsive UI
- Axios - HTTP client
- Zustand - State management
- Google Maps API - Location services
- React Icons - Icon library
- Date-fns - Date manipulation

**Backend**
- Flask 2.3.3 - Python web framework
- Flask-Cors - Cross-origin support
- Flask-JWT-Extended - JWT authentication
- PyMongo 4.5 - MongoDB driver
- Twilio - SMS notifications
- Werkzeug - Security utilities

**Database**
- MongoDB - NoSQL database (flexible schema for donations)
- Collections: users, donations, ngos, feedback

**Authentication**
- JWT (JSON Web Tokens)
- Bcrypt for password hashing
- Role-based access control (donor, ngo, admin)

**Deployment**
- Backend: Heroku, Render, or AWS
- Frontend: Vercel, Netlify, or AWS
- Database: MongoDB Atlas (cloud)

---

## 📂 Project Structure

```
annadan-a-umeed/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app creation & config
│   │   ├── models/
│   │   │   ├── user.py          # User model (Donor/NGO)
│   │   │   ├── donation.py      # Donation model
│   │   │   ├── feedback.py      # Feedback model
│   │   │   └── ngo.py           # NGO specific model
│   │   ├── routes/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── donor.py         # Donor endpoints
│   │   │   ├── ngo.py           # NGO endpoints
│   │   │   ├── admin.py         # Admin endpoints
│   │   │   └── feedback.py      # Feedback endpoints
│   │   └── utils/
│   │       ├── auth.py          # JWT utilities
│   │       ├── validators.py    # Input validation
│   │       └── notifications.py # Email/SMS service
│   ├── run.py                   # Entry point
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment template
│
├── frontend/
│   ├── public/
│   │   └── index.html           # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.js        # Navigation component
│   │   ├── pages/
│   │   │   ├── Home.js          # Landing page
│   │   │   ├── Login.js         # Login page
│   │   │   ├── Register.js      # Registration page
│   │   │   ├── Dashboard.js     # User dashboard
│   │   │   └── PostFood.js      # Post donation page
│   │   ├── utils/
│   │   │   ├── api.js           # API client
│   │   │   └── store.js         # Zustand store
│   │   ├── App.js               # Main app component
│   │   ├── App.css              # App styles
│   │   ├── index.js             # React entry point
│   │   └── index.css            # Global styles
│   ├── package.json             # Dependencies
│   └── .env.example             # Environment template
│
└── README.md                    # This file
```

---

## 🐙 Version Control (GitHub)

The project includes a strongly configured `.gitignore` to prevent secret leaks and unnecessary uploads. When pushing your repository to remote platforms like GitHub, keep in mind:

- **DO NOT** commit `.env` or `.env.local` files! (They are ignored automatically by `.gitignore` to protect API keys and database URLs).
- **DO NOT** commit dependency folders like `node_modules/` or `backend/venv/`.
- **DO** commit lock files (like `package-lock.json` and `requirements.txt`) to ensure dependencies are replicated correctly across environments.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+ and npm
- MongoDB account (MongoDB Atlas)
- Google Maps API key
- Twilio account (optional)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # Mac/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```
   
   **Fill in your credentials:**
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/annadan_db
   JWT_SECRET_KEY=your_super_secret_key_here
   GOOGLE_MAPS_API_KEY=your_api_key
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```

5. **Run Flask server:**
   ```bash
   python run.py
   ```
   Server runs at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```
   
   **Fill in your credentials:**
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   ```

4. **Start React development server:**
   ```bash
   npm start
   ```
   App runs at `http://localhost:3000`

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (donor/NGO)
- `POST /api/auth/login` - Login user
- `GET /api/auth/verify-email/<token>` - Verify email
- `POST /api/auth/logout` - Logout user

### Donor Endpoints
- `POST /api/donors/post-food` - Post new food donation
- `GET /api/donors/my-donations` - Get donor's donations
- `GET /api/donors/donation/<id>` - Get donation details
- `PUT /api/donors/donation/<id>` - Update donation
- `POST /api/donors/donation/<id>/cancel` - Cancel donation

### NGO Endpoints
- `GET /api/ngos/nearby-food` - Find food nearby
- `POST /api/ngos/donation/<id>/accept` - Accept donation
- `GET /api/ngos/my-collections` - Get NGO's collections
- `POST /api/ngos/donation/<id>/collected` - Mark as collected
- `GET /api/ngos/profile` - Get NGO profile
- `PUT /api/ngos/profile` - Update NGO profile

### Feedback Endpoints
- `POST /api/feedback/submit` - Submit feedback
- `GET /api/feedback/user/<id>` - Get user feedback
- `GET /api/feedback/donation/<id>` - Get donation feedback
- `GET /api/feedback/leaderboard` - Get top NGOs leaderboard

### Admin Endpoints
- `GET /api/admin/dashboard` - Get statistics
- `GET /api/admin/users` - Get all users
- `POST /api/admin/ngos/verify/<id>` - Verify NGO
- `GET /api/admin/donations/analytics` - Get analytics
- `POST /api/admin/user/<id>/deactivate` - Deactivate user

---

## 🗄️ Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique),
  phone: String (unique),
  password: String (hashed),
  name: String,
  user_type: String (donor/ngo/admin),
  address: String,
  city: String,
  state: String,
  is_active: Boolean,
  is_admin: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Donations Collection
```javascript
{
  _id: ObjectId,
  donor_id: ObjectId (ref: users),
  food_type: String,
  quantity: Number,
  unit: String (kg/ltr/plates/boxes),
  description: String,
  pickup_time: DateTime,
  expiry_time: DateTime,
  location: {
    address: String,
    city: String,
    coordinates: [longitude, latitude]
  },
  donor_name: String,
  donor_phone: String,
  status: String (available/accepted/collected/completed/cancelled),
  accepted_by: ObjectId (ref: users),
  accepted_at: DateTime,
  created_at: DateTime,
  updated_at: DateTime
}
```

### NGOs Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: users, unique),
  name: String,
  organization_name: String,
  phone: String,
  email: String,
  location: {
    address: String,
    city: String,
    coordinates: [longitude, latitude]
  },
  verified: Boolean,
  total_pickups: Number,
  rating: Number,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Feedback Collection
```javascript
{
  _id: ObjectId,
  donation_id: ObjectId (ref: donations),
  from_user_id: ObjectId (ref: users),
  from_user_type: String (donor/ngo),
  to_user_id: ObjectId (ref: users),
  rating: Number (1-5),
  comment: String,
  food_quality: String,
  punctuality: String,
  communication: String,
  created_at: DateTime
}
```

---

## 🔐 Security Features

- **Password Hashing**: Bcrypt with salt rounds
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Restricted cross-origin requests
- **Input Validation**: Server-side validation of all inputs
- **Role-Based Access**: Different permissions per user type
- **SQL Injection Prevention**: Using parameterized queries with MongoDB
- **Environment Variables**: Sensitive data in .env files

---

## 🎨 UI/UX Features

- **Responsive Design**: Mobile, tablet, and desktop friendly
- **Modern Aesthetics**: Gradient headers, smooth animations
- **Intuitive Navigation**: Clear user flows
- **Form Validation**: Real-time feedback
- **Loading States**: User feedback during operations
- **Error Handling**: Clear error messages
- **Dark Mode Ready**: CSS variables for theming

---

## 🚀 Future Enhancements

### Phase 2
- [ ] Real-time notifications using WebSockets
- [ ] Advanced filtering (food preferences, allergens)
- [ ] Image upload for food donations
- [ ] Mobile app (React Native/Flutter)
- [ ] SMS alerts integration
- [ ] Push notifications with FCM

### Phase 3
- [ ] Food quality image analysis (CNN)
- [ ] Demand prediction AI model
- [ ] Integration with municipal bodies
- [ ] Leaderboard with achievements
- [ ] Video pickup verification
- [ ] Carbon footprint tracking

### Phase 4
- [ ] IoT temperature sensors for containers
- [ ] Blockchain for transparency
- [ ] Multi-language support
- [ ] Integration with food delivery APIs
- [ ] Corporate dashboard for bulk donors

---

## 📊 Key Metrics Tracked

- Total food saved (kg)
- Number of pickups completed
- NGOs helped
- Donors engaged
- Average food quality ratings
- Response time (donor to NGO)
- Food waste reduction percentage
- Community impact

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is open source under MIT License. See LICENSE file for details.

---

## 🌟 Inspiration

This project is inspired by:
- Food for All initiatives
- UN Sustainable Development Goal 12 (Responsible Consumption)
- Local NGO efforts in food redistribution
- Community-driven social impact

---

## 📞 Support & Contact

For questions, bugs, or suggestions:
- Email: support@annadan-umeed.com
- Issues: GitHub Issues
- Twitter: @AnnadanUmeed

---

## 🙏 Acknowledgments

- Thanks to all food donors for their generosity
- Thanks to NGOs for their tireless work
- Thanks to volunteers who help redistribute
- Thanks to the open-source community

---

**Made with ❤️ to fight hunger and reduce waste**
