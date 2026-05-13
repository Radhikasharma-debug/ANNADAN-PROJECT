# Getting Started Checklist 🚀

## Pre-Setup Checklist

### System Requirements
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 14+ & npm installed (`node --version`, `npm --version`)
- [ ] Git installed (`git --version`)
- [ ] Text editor/IDE (VS Code recommended)
- [ ] Internet connection
- [ ] ~500MB free disk space

### Accounts & API Keys (Get these first!)
- [ ] MongoDB Atlas account created (free tier)
- [ ] Google Maps API key obtained
- [ ] (Optional) Twilio account for SMS
- [ ] (Optional) Gmail app password for email notifications

---

## Backend Setup Checklist

### Step 1: Navigate & Create Environment
- [ ] Open terminal/PowerShell
- [ ] Run: `cd backend`
- [ ] Run: `python -m venv venv`
- [ ] Run: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
- [ ] Verify: `(venv)` appears in terminal

### Step 2: Install Dependencies
- [ ] Run: `pip install -r requirements.txt`
- [ ] Wait for installation to complete (2-3 minutes)
- [ ] Run: `pip list` to verify installations

### Step 3: Configure Environment
- [ ] Run: `cp .env.example .env`
- [ ] Open `.env` in text editor
- [ ] [ ] Set `MONGODB_URI` with your MongoDB connection string
- [ ] [ ] Set `JWT_SECRET_KEY` to any random string (min 32 chars)
- [ ] [ ] Set `GOOGLE_MAPS_API_KEY`
- [ ] [ ] (Optional) Set Twilio credentials
- [ ] [ ] (Optional) Set email credentials
- [ ] Save `.env` file

### Step 4: Start Backend
- [ ] Run: `python run.py`
- [ ] [ ] You should see:
  - `✓ Connected to MongoDB`
  - `Running on http://127.0.0.1:5000`
- [ ] Leave this terminal running
- [ ] **Backend is READY** ✅

---

## Frontend Setup Checklist

### Step 1: New Terminal Window
- [ ] Open NEW terminal/PowerShell
- [ ] Run: `cd frontend`
- [ ] Do NOT activate venv (only for backend)

### Step 2: Install Dependencies
- [ ] Run: `npm install`
- [ ] Wait for installation (5-10 minutes, first time)
- [ ] Wait for: `added XX packages`

### Step 3: Configure Environment
- [ ] Run: `cp .env.example .env`
- [ ] Open `.env` in text editor
- [ ] [ ] Set `REACT_APP_API_URL=http://localhost:5000/api`
- [ ] [ ] Set `REACT_APP_GOOGLE_MAPS_API_KEY`
- [ ] Save `.env` file

### Step 4: Start Frontend
- [ ] Run: `npm start`
- [ ] Browser should auto-open to `http://localhost:3000`
- [ ] [ ] You should see:
  - Home page with "Annadan - A Umeed"
  - Navigation bar
  - Get Started button
- [ ] **Frontend is READY** ✅

---

## First Test Run Checklist

### Test 1: Register as Donor
- [ ] Click "Get Started" button
- [ ] Click "Register"
- [ ] Select "🎁 Donor" tab
- [ ] Fill form with:
  - Name: `Test Donor`
  - Email: `donor@test.com`
  - Phone: `+919876543210`
  - Password: `DonorPass123` (min 6 chars, 1 uppercase, 1 digit)
- [ ] Click "Register as Donor"
- [ ] Success message appears
- [ ] Redirected to login page

### Test 2: Login as Donor
- [ ] Email: `donor@test.com`
- [ ] Password: `DonorPass123`
- [ ] Click "Login"
- [ ] Dashboard appears
- [ ] "Welcome, Test Donor!" message shows
- [ ] "Post Food" button visible

### Test 3: Post a Donation
- [ ] Click "Post Food"
- [ ] Fill form:
  - Food Type: `Biryani`
  - Quantity: `25`
  - Unit: `plates`
  - Description: `Fresh catered biryani`
  - Address: `Hotel XYZ`
  - City: `New Delhi`
  - Phone: `+919876543210`
  - Latitude: `28.6139`
  - Longitude: `77.2090`
  - Pickup Time: (any future date/time)
- [ ] Click "Post Food Donation"
- [ ] Success message appears
- [ ] Redirected to dashboard

### Test 4: Register as NGO
- [ ] Logout (click Logout button)
- [ ] Click "Get Started"
- [ ] Click "Register"
- [ ] Select "🤝 NGO" tab
- [ ] Fill form with:
  - Organization: `Care Foundation`
  - Contact Name: `Jane NGO`
  - Email: `ngo@test.com`
  - Phone: `+919876543211`
  - Password: `NgoPass123`
- [ ] Click "Register as NGO"
- [ ] Success message

### Test 5: Login as NGO & Find Food
- [ ] Login as `ngo@test.com` / `NgoPass123`
- [ ] Dashboard appears
- [ ] "Find Food Nearby" button visible
- [ ] Click "Find Food Nearby"
- [ ] Should see the Biryani donation you posted earlier
- [ ] Distance should be calculated and shown

### Test 6: Accept Donation
- [ ] Click on the food listing
- [ ] Click "Accept" button
- [ ] Status changes to "accepted"
- [ ] Success message appears

---

## Database Verification Checklist

### MongoDB Atlas
- [ ] Log into MongoDB Atlas
- [ ] Go to Collections
- [ ] [ ] Database: `annadan_db`
- [ ] [ ] Collections created:
  - [ ] `users` (should have 2 documents)
  - [ ] `donations` (should have 1 document)
  - [ ] `ngos` (should have 1 document)
  - [ ] `feedback` (empty for now)
- [ ] Click on `users` collection
- [ ] Should see your donor and NGO records

---

## API Testing Checklist

### Test with Postman/cURL

- [ ] Health Check (GET)
  ```
  GET http://localhost:5000/api/health
  ```
  Expected: `{"status": "healthy"}`

- [ ] Login (POST)
  ```
  POST http://localhost:5000/api/auth/login
  Headers: Content-Type: application/json
  Body: {"email": "donor@test.com", "password": "DonorPass123"}
  ```
  Expected: token received

- [ ] My Donations (GET)
  ```
  GET http://localhost:5000/api/donors/my-donations
  Headers: Authorization: Bearer <YOUR_TOKEN>
  ```
  Expected: array of donations

---

## Troubleshooting Checklist

### Backend Won't Start
- [ ] Check Python version: `python --version`
- [ ] Check venv activated: `(venv)` in terminal
- [ ] Check requirements installed: `pip list | grep Flask`
- [ ] Check .env file exists
- [ ] Check MongoDB connection string
- [ ] Check port 5000 not in use

### Frontend Won't Start
- [ ] Check Node version: `node --version`
- [ ] Check npm version: `npm --version`
- [ ] Check node_modules exist: `ls node_modules` (or `dir` on Windows)
- [ ] Check .env file created
- [ ] Check API_URL is correct
- [ ] Check port 3000 not in use

### Cannot Login
- [ ] Check email/password match registration
- [ ] Check MongoDB is connected
- [ ] Check backend logs for errors
- [ ] Try registering again

### MongoDB Connection Failed
- [ ] Check connection string in .env
- [ ] Verify username/password are correct
- [ ] Check IP whitelist on MongoDB Atlas (add 0.0.0.0)
- [ ] Check internet connection
- [ ] Check VPN/firewall not blocking

---

## Documentation Review Checklist

Read these in order:
1. [ ] **README.md** - Full project overview
2. [ ] **QUICK_START.md** - Quick setup guide
3. [ ] **API_DOCUMENTATION.md** - All endpoints
4. [ ] **DEPLOYMENT_GUIDE.md** - Production setup
5. [ ] **PROJECT_SUMMARY.md** - Project overview

---

## Development Environment Setup

### VS Code Extensions (Recommended)
- [ ] Install Python extension
- [ ] Install Flask extension
- [ ] Install ES7+ React extension
- [ ] Install REST Client extension
- [ ] Install MongoDB for VS Code

### Terminal Setup
- [ ] Terminal 1: Backend running
- [ ] Terminal 2: Frontend running
- [ ] Terminal 3: (optional) for git commands

---

## Next Phase Checklist

Once everything works:

### Customization
- [ ] Update colors in `index.css`
- [ ] Change logo in `Navbar.js`
- [ ] Update donation types
- [ ] Add your organization name

### New Features
- [ ] [ ] Add map view for food locations
- [ ] [ ] Add notification system
- [ ] [ ] Add image uploads
- [ ] [ ] Add advanced search filters

### Deployment Prep
- [ ] [ ] Set up GitHub repository
- [ ] [ ] Create Heroku account
- [ ] [ ] Create Vercel account
- [ ] [ ] Update production API URLs
- [ ] [ ] Set up environment variables

---

## Success Criteria ✅

You'll know everything is working when:

- ✅ Both servers running without errors
- ✅ Can register as donor and NGO
- ✅ Can login with credentials
- ✅ Can post food donations
- ✅ Can see donations in MongoDB
- ✅ Can find food as NGO
- ✅ Can accept donations
- ✅ Can rate and review

---

## Quick Commands Reference

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py

# Frontend
cd frontend
npm install
npm start

# Database (mongosh)
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/annadan_db"
show collections
db.users.find()
```

---

## Still Stuck?

1. Check the error message carefully
2. Google the error
3. Check the documentation files
4. Review the code comments
5. Check backend logs
6. Check browser console (F12)

---

## 🎉 You're Ready to Go!

Once you check all boxes, you have a **fully functional** food redistribution platform!

Next: Follow the DEPLOYMENT_GUIDE.md to deploy online.

---

**Congratulations on your project! 🚀**
