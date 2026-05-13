# Annadan - Comprehensive Code Audit and Fixes

## Summary of Issues Found and Fixed

### 1. **Frontend API Client Error Handling**
**Problem:** Error responses from the backend were not being properly extracted. The fetch response was not being parsed before checking `.ok`.

**Fix:** Updated `frontend/src/utils/api.js`:
- Parse JSON response BEFORE checking status
- Attach response data to error object
- Extract error message properly for display

### 2. **Backend Requirements.txt Mismatch**
**Problem:** `requirements.txt` listed FastAPI, PostgreSQL, and asyncio packages but the app uses Flask and MongoDB.

**Fix:** Replaced with correct dependencies:
```
Flask==2.3.3
Flask-CORS==4.0.0
Flask-JWT-Extended==4.5.2
PyMongo==4.5.0
python-dotenv==1.0.0
bcrypt==4.0.1
Werkzeug==2.3.7
Twilio==8.10.0
geopy==2.3.0
Flask-Mail==0.9.1
PyJWT>=2.0,<3.0
```

### 3. **Missing .env Files**
**Problem:** Backend couldn't connect to MongoDB because `.env` file was missing.

**Fix:** Created:
- `backend/.env` with MongoDB URI and JWT secrets
- `frontend/.env.local` with API URL and Google Maps key

### 4. **ObjectId vs String Mismatches**
**Problem:** Inconsistent handling of user IDs and donation IDs:
- JWT tokens store user_id as STRING
- Models were trying to convert strings to ObjectId unnecessarily
- Foreign key fields (donor_id, accepted_by, user_id) were being stored/queried inconsistently

**Fixes Applied:**
- Updated `NGO.find_by_user_id()` to query by string, not ObjectId
- Updated `Donation.find_by_donor()` to query by string, not ObjectId
- Updated `Feedback.find_by_donation()` and `find_for_user()` to use strings
- Updated `Donation.accept_donation()` to store ngo_id as string
- Updated `User.find_by_id()` to handle both string and ObjectId conversions

### 5. **Login/Register Error Display**
**Problem:** Specific backend errors were not shown to users (only "BAD REQUEST").

**Fix:** Updated frontend error handlers in:
- `frontend/src/pages/Login.js` - shows backend error message
- `frontend/src/pages/Register.js` - shows backend error message
- Both log full error to console for debugging

### 6. **NGO Profile Creation**
**Problem:** When creating NGO profile during registration, null pointer on missing profile.

**Fix:** Added null check in `backend/app/routes/ngo.py` before calling `increment_pickups()`

## Verification Checklist

### Backend Setup
- [ ] Created `backend/.env` with MongoDB connection string
- [ ] Installed correct dependencies: `pip install -r requirements.txt`
- [ ] MongoDB Atlas cluster accessible and connection string works

### Test Registration Flow
Use this test data:
```
User Type: Donor
Name: Radhika Sharma
Email: radhika05@gmail.com
Phone: 9755899705
Password: Test123 (must have uppercase + digit)
Address: 123 MG Road, Indiranagar, Bengaluru, Karnataka 560038
City: Bengaluru
```

Expected: User created in MongoDB, can proceed to login

### Test Login Flow
```
Email: radhika05@gmail.com
Password: Test123
```

Expected: JWT token generated, user redirected to dashboard

### Test Donor Flow
1. Login as donor
2. Click "Post Food"
3. Fill in donation details
4. Submit
5. Check "My Donations" dashboard shows the donation

### Test NGO Flow
1. Register as NGO:
   - Organization Name: "Help India Foundation"
   - Contact: Radhika Sharma
   - Email: ngo@example.com
   - Phone: 9876543210
   - City: Bengaluru
2. Login
3. View nearby food donations
4. Accept a donation
5. Check status changes to "accepted"

## Code Changes Summary

| File | Change | Reason |
|------|--------|--------|
| `frontend/src/utils/api.js` | Parse response before checking status | Extract backend error messages |
| `frontend/src/pages/Login.js` | Show err.message instead of generic text | Better error feedback |
| `frontend/src/pages/Register.js` | Show err.message instead of generic text | Better error feedback |
| `backend/requirements.txt` | Replace FastAPI with Flask+MongoDB deps | Match actual stack |
| `backend/.env` | Created with MongoDB URI | Enable database connection |
| `frontend/.env.local` | Created with API URL | Connect to backend |
| `backend/app/models/ngo.py` | find_by_user_id() queries by string | Fix ObjectId mismatch |
| `backend/app/models/donation.py` | find_by_donor() queries by string | Fix ObjectId mismatch |
| `backend/app/models/donation.py` | accept_donation() stores ngo_id as string | Fix ObjectId mismatch |
| `backend/app/models/feedback.py` | find_by_donation/find_for_user use strings | Fix ObjectId mismatch |
| `backend/app/models/user.py` | find_by_id() handles string conversion | Proper ID lookup |
| `backend/app/routes/ngo.py` | Add null check before increment_pickups | Prevent null pointer |

## How to Test Complete Flow

### Terminal 1 - Backend
```powershell
cd "D:\web dev\annadan-a-umeed\backend"
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt  # Fresh install with correct deps
python run.py
```

Should see:
```
✓ Connected to MongoDB: annadan_db
 * Running on http://0.0.0.0:5000
```

### Terminal 2 - Frontend
```powershell
cd "D:\web dev\annadan-a-umeed\frontend"
npm install  # Fresh install
npm start
```

Should open browser to `http://localhost:3000`

### Browser Testing
1. Go to Register page
2. Fill in test donor data (above)
3. Should register successfully
4. Should redirect to Login
5. Login with credentials
6. Should see Dashboard with "Post Food" button
7. Dashboard should load data without errors

## Debugging Tips

### Check Browser Console (F12)
- Look for any error messages logged by improved error handlers
- Check Network tab → /api/auth/register response for exact backend error
- Check if API_URL in .env.local matches backend port (5000)

### Check Backend Console
- Watch for MongoDB connection messages
- Look for validation errors when processing requests
- Check for any exception stack traces

### Common Issues

**"Cannot find module 'flask'"**
→ Activate venv and reinstall: `pip install -r requirements.txt`

**"MongoDB Connection Error"**
→ Check MongoDB URI in .env, verify IP in Atlas Network Access

**"API Error: BAD REQUEST" without details**
→ Check browser console and Network tab for actual error response

**"User not found after registration"**
→ Check MongoDB collections: `db.users.find()`

**"Nearby food empty for NGO"**
→ NGO must have location coordinates set (latitude/longitude from registration)
→ Ensure donor donation has valid coordinates
