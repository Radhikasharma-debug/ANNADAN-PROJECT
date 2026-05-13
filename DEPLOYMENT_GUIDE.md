# Development & Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.8+
- Node.js 14+ and npm
- Git
- MongoDB Atlas account
- Code editor (VS Code recommended)

### Step 1: Clone & Setup Backend

```bash
# Navigate to project
cd annadan-a-umeed/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your credentials
# (See Configuration section below)

# Run Flask server
python run.py
```

Server starts at: `http://localhost:5000`

### Step 2: Setup Frontend

```bash
# Open new terminal, navigate to frontend
cd annadan-a-umeed/frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env and add API URL
# REACT_APP_API_URL=http://localhost:5000/api

# Start React development server
npm start
```

App opens at: `http://localhost:3000`

---

## Configuration

### Backend Environment Variables (.env)

```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=True

# MongoDB (MongoDB Atlas)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/annadan_db?retryWrites=true&w=majority
MONGODB_DB_NAME=annadan_db

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_min_32_chars
JWT_ACCESS_TOKEN_EXPIRES=3600

# Google Maps API
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Twilio (optional for SMS)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Session Secret
SECRET_KEY=your_secret_key_for_sessions
```

### Frontend Environment Variables (.env)

```bash
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

---

## Getting API Keys

### 1. Google Maps API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable "Maps JavaScript API" and "Geocoding API"
4. Create API key (Application Restrictions: HTTP referrers)
5. Copy and paste in .env

### 2. MongoDB Atlas

1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new project
3. Create a cluster (free tier available)
4. Create database user with password
5. Get connection string
6. Replace in .env: `mongodb+srv://username:password@cluster.mongodb.net/...`

### 3. Twilio (Optional)

1. Sign up at [Twilio](https://www.twilio.com)
2. Get Account SID and Auth Token from dashboard
3. Get a phone number for SMS
4. Add to .env

---

## Development Workflow

### Running Both Servers

```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate  # or source venv/bin/activate
python run.py

# Terminal 2: Frontend
cd frontend
npm start
```

### Testing API Endpoints

Use Postman or cURL:

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "phone": "+91-9876543210",
    "name": "Test User",
    "user_type": "donor"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### Database Management

```bash
# Connect to MongoDB in mongosh:
mongosh "mongodb+srv://username:password@cluster.mongodb.net/annadan_db"

# View collections
show collections

# Check documents
db.users.find().pretty()
db.donations.find().pretty()

# Clear data (careful!)
db.donations.deleteMany({})
```

---

## Production Deployment

### Backend Deployment (Heroku Example)

1. **Create Heroku account** at [heroku.com](https://heroku.com)

2. **Install Heroku CLI**
   ```bash
   # Download and install from heroku.com/download
   ```

3. **Prepare backend**
   ```bash
   cd backend
   
   # Create Procfile
   echo "web: gunicorn run:app" > Procfile
   
   # Add gunicorn to requirements.txt
   echo "gunicorn==21.2.0" >> requirements.txt
   
   # Initialize git repo
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. **Deploy**
   ```bash
   # Login
   heroku login
   
   # Create app
   heroku create your-app-name
   
   # Set environment variables
   heroku config:set MONGODB_URI=your_mongodb_uri
   heroku config:set JWT_SECRET_KEY=your_secret_key
   # ... set all other variables
   
   # Deploy
   git push heroku main
   
   # View logs
   heroku logs --tail
   ```

### Frontend Deployment (Vercel Example)

1. **Create Vercel account** at [vercel.com](https://vercel.com)

2. **Push frontend to GitHub**

3. **Import project in Vercel**
   - Connect GitHub account
   - Select repository
   - Set build command: `npm run build`
   - Set output directory: `build`

4. **Set Environment Variables**
   - Add `REACT_APP_API_URL` pointing to deployed backend

5. **Deploy** - Automatic on git push

### Database (MongoDB Atlas)

1. Create cluster on MongoDB Atlas
2. Get connection string
3. Set whitelist IP to allow all (0.0.0.0) for production
4. Create backup policies

---

## Performance Optimization

### Backend
```python
# Add caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Add pagination to all list endpoints
# Add database indexes
# Use connection pooling
```

### Frontend
```javascript
// Code splitting
const Dashboard = React.lazy(() => import('./pages/Dashboard'));

// Image optimization
<img src={url} loading="lazy" />

// Memoization for components
React.memo(Component)
```

---

## Monitoring & Logging

### Backend Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Donation created")
logger.error("Database connection failed")
```

### Frontend Error Tracking
```javascript
// Add Sentry for error tracking
import * as Sentry from "@sentry/react";

Sentry.captureException(error);
```

---

## Testing

### Backend Tests
```bash
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=app
```

### Frontend Tests
```bash
npm test

# With coverage
npm test -- --coverage
```

---

## Troubleshooting

### Port Already in Use
```bash
# Windows - Find process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

### MongoDB Connection Issues
- Check connection string in .env
- Verify IP whitelist on Atlas
- Check network connectivity
- Verify username/password

### CORS Errors
- Backend .env: `FLASK_CORS_ORIGINS=*` for dev
- Frontend: Use `/api` proxy in development
- Set proper `FLASK_CORS_ALLOWED_ORIGINS` for production

### JWT Token Errors
- Verify JWT_SECRET_KEY is set
- Check token expiry time
- Ensure Authorization header format: `Bearer <token>`

---

## Maintenance

### Regular Tasks
- [ ] Monitor server logs
- [ ] Check database size
- [ ] Backup MongoDB regularly
- [ ] Update dependencies (`pip list --outdated`, `npm outdated`)
- [ ] Review error rates
- [ ] Check API response times

### Security Updates
```bash
# Backend
pip install --upgrade pip
pip install -U Flask Flask-Cors Flask-JWT-Extended

# Frontend
npm update
npm audit fix
```

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev)
- [MongoDB Docs](https://docs.mongodb.com/)
- [Heroku Docs](https://devcenter.heroku.com/)
- [Vercel Docs](https://vercel.com/docs)

---

Need help? Check logs and error messages first! 🚀
