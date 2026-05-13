# Quick Start Guide - Annadan Platform

## 🚀 Get Running in 5 Minutes

### Prerequisites Check
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 14+ installed (`node --version`)
- [ ] MongoDB Atlas account created
- [ ] Google Maps API key obtained

---

## Start Backend (Terminal 1)

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup .env file
cp .env.example .env

# ⚠️ IMPORTANT: Edit .env with your credentials:
#   - MONGODB_URI=<your_mongodb_connection_string>
#   - JWT_SECRET_KEY=<any_random_string_min_32_chars>
#   - GOOGLE_MAPS_API_KEY=<your_key>

# Start server
python run.py
# ✅ Server running at http://localhost:5000
```

---

## Start Frontend (Terminal 2)

```bash
cd frontend

# Install dependencies
npm install

# Setup .env file
cp .env.example .env

# ⚠️ IMPORTANT: Edit .env:
#   - REACT_APP_API_URL=http://localhost:5000/api

# Start app
npm start
# ✅ App running at http://localhost:3000
```

---

## Test the App

### 1. Register as Donor
- Go to http://localhost:3000
- Click "Register"
- Select "🎁 Donor" tab
- Fill form and register
- Username: `test@donor.com` / Password: `DonorPass123`

### 2. Register as NGO
- Click "Register" again
- Select "🤝 NGO" tab
- Fill form and register
- Username: `test@ngo.com` / Password: `NgoPass123`

### 3. Login & Test
- **As Donor:**
  - Login
  - Click "Post Food"
  - Fill donation details
  - Submit

- **As NGO:**
  - Login
  - View "Find Food Nearby"
  - Should see the posted donation

---

## API Endpoints to Test

```bash
# 1. Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123","phone":"+919876543210","name":"Test","user_type":"donor"}'

# 2. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123"}'
# Copy the token from response

# 3. Post Food (replace TOKEN)
curl -X POST http://localhost:5000/api/donors/post-food \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"food_type":"Biryani","quantity":25,"unit":"plates","latitude":28.6139,"longitude":77.2090,"address":"Hotel XYZ","city":"Delhi","donor_phone":"+919876543210","pickup_time":"2024-01-20T18:00:00"}'

# 4. Get Dashboard Stats
curl -X GET http://localhost:5000/api/admin/dashboard \
  -H "Authorization: Bearer TOKEN"
```

---

## Folder Structure

```
annadan-a-umeed/
├── backend/              ← Flask API Server
│   ├── app/
│   │   ├── models/       ← Database models
│   │   ├── routes/       ← API endpoints
│   │   └── utils/        ← Helpers & utilities
│   └── run.py            ← Start here
│
├── frontend/             ← React Web App
│   ├── src/
│   │   ├── pages/        ← Page components
│   │   ├── components/   ← Reusable components
│   │   └── utils/        ← Helper functions
│   └── package.json
│
├── README.md             ← Full documentation
├── API_DOCUMENTATION.md  ← API reference
└── DEPLOYMENT_GUIDE.md   ← Production setup
```

---

## Common Issues & Fixes

### ❌ "Cannot connect to MongoDB"
```
✅ Solution:
1. Check MONGODB_URI in .env is correct
2. Verify IP whitelist on MongoDB Atlas (add 0.0.0.0)
3. Check internet connection
```

### ❌ "Port 5000 already in use"
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

### ❌ "CORS errors in browser"
```
✅ Solution:
1. Backend is running on localhost:5000
2. Frontend is running on localhost:3000
3. Check REACT_APP_API_URL in .env
```

### ❌ "Invalid token" error
```
✅ Solution:
1. Login again to get new token
2. Copy full token including "Bearer "
3. Check token hasn't expired
```

---

## Next Steps

1. **Add more features:**
   - [ ] Find food map view
   - [ ] Pickup tracking
   - [ ] Notifications
   - [ ] User ratings

2. **Improve UX:**
   - [ ] Dark mode
   - [ ] Mobile responsiveness
   - [ ] Animations

3. **Deploy:**
   - [ ] Backend to Heroku
   - [ ] Frontend to Vercel
   - [ ] Setup MongoDB Atlas

4. **Advanced:**
   - [ ] AI image analysis for food
   - [ ] Real-time notifications
   - [ ] Mobile app

---

## Documentation Files

- 📖 **README.md** - Full project overview
- 📡 **API_DOCUMENTATION.md** - All API endpoints
- 🚀 **DEPLOYMENT_GUIDE.md** - Production setup
- 📝 **QUICK_START.md** - This file!

---

## 💡 Tips

- Use VS Code REST Client extension to test APIs
- Use MongoDB Compass to view database
- Enable debug mode in Flask for better errors
- Check browser console for frontend errors

---

## Support

- Backend Issues? Check: `http://localhost:5000/api/health`
- Frontend Issues? Check: Browser Developer Tools (F12)
- Database Issues? Check: MongoDB Atlas dashboard

---

## 🎉 You're Ready!

Start coding and building amazing features! 🚀

Questions? Check the full README.md for detailed documentation.
