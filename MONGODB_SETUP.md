# MongoDB Setup & Configuration Guide 🗄️

## Overview
This guide covers setting up and managing MongoDB for the Annadan-A-Umeed platform using MongoDB Compass (Visual Management Tool) and proper configuration practices.

---

## Part 1: MongoDB Atlas Setup

### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new project (e.g., "Annadan-Umeed")
4. Select the free tier (M0 - Sandbox)

### Step 2: Create a Cluster
1. In MongoDB Atlas, click "Build a Database"
2. Choose **Shared** cluster (Free tier)
3. Select your preferred region (e.g., AWS, closest to your location)
4. Name your cluster (e.g., `annadancluster`)
5. Wait for cluster to be created (~2-3 minutes)

### Step 3: Create Database User
1. Go to **Database Access** in the left menu
2. Click **Add New User**
3. Set username: `annadan_user`
4. Set password: (use a strong password, save it!)
5. Permissions: **Read and write to any database**
6. Click **Add User**

### Step 4: Whitelist IP Addresses
1. Go to **Network Access** in the left menu
2. Click **Add IP Address**
3. Select **Allow Access from Anywhere** (for dev), OR
4. Add specific IPs only (for production)
5. Click **Confirm**

### Step 5: Get Connection String
1. Go back to **Clusters** page
2. Click **Connect** next to your cluster
3. Select **Drivers** (not Compass from here)
4. Copy the connection string
5. Replace `<password>` and `<username>` with your credentials

**Example Connection String:**
```
mongodb+srv://annadan_user:YOUR_PASSWORD@annadancluster.xxxxx.mongodb.net/annadan_db?retryWrites=true&w=majority
```

---

## Part 2: Using MongoDB Compass (Visual Tool)

### Download & Install
1. Go to [MongoDB Compass Download](https://www.mongodb.com/products/compass)
2. Download appropriate version (Windows/Mac/Linux)
3. Install the application

### Connect with Compass
1. **Open MongoDB Compass**
2. Click "**New Connection**" or "**Connect**" button
3. **Select connection method: URI**
4. Paste your connection string:
   ```
   mongodb+srv://annadan_user:YOUR_PASSWORD@annadancluster.xxxxx.mongodb.net/annadan_db?retryWrites=true&w=majority
   ```
5. Click **Connect**

### Verify Connection
Once connected, you should see:
- ✓ Your cluster name
- ✓ Databases listed below
- ✓ "**annadan_db**" database

---

## Part 3: Database Schema & Collections

### Collections Structure

#### 1. **users** Collection
Stores user (donor/recipient) information
```javascript
{
  _id: ObjectId,
  email: "user@example.com",      // Unique
  phone: "+1234567890",            // Unique, sparse
  password_hash: "hashed_password",
  first_name: "John",
  last_name: "Doe",
  user_type: "donor",              // 'donor', 'ngo', 'admin'
  address: "123 Main St, City",
  city: "New York",
  state: "NY",
  pincode: "10001",
  location: {type: "Point", coordinates: [-73.935242, 40.730610]},
  is_verified: false,
  verification_token: "token_hash",
  created_at: ISODate("2024-01-01T10:00:00Z"),
  updated_at: ISODate("2024-01-01T10:00:00Z"),
  is_active: true
}
```

#### 2. **donations** Collection
Tracks food donations from donors
```javascript
{
  _id: ObjectId,
  donor_id: ObjectId,              // Reference to users
  food_type: "Meals",              // 'Meals', 'Raw Food', 'Fruits', 'Vegetables'
  quantity: 50,                    // in servings
  description: "Cooked rice and curry",
  image_url: "https://...",
  location: {type: "Point", coordinates: [-73.935242, 40.730610]},
  address: "123 Main St, City",
  status: "available",             // 'available', 'accepted', 'collected', 'completed'
  accepted_by: ObjectId,           // Reference to NGO (null if not accepted)
  pickup_date: ISODate("2024-01-02T15:00:00Z"),
  pickup_time: "3:00 PM - 5:00 PM",
  expiry: ISODate("2024-01-02T09:00:00Z"),  // Food expiry time
  special_instructions: "Keep refrigerated",
  created_at: ISODate("2024-01-01T10:00:00Z"),
  updated_at: ISODate("2024-01-01T10:00:00Z")
}
```

#### 3. **ngos** Collection
Stores NGO/Organization information
```javascript
{
  _id: ObjectId,
  email: "ngo@example.com",        // Unique
  phone: "+1234567890",
  password_hash: "hashed_password",
  organization_name: "Hope Foundation",
  registration_number: "REG123456",
  address: "456 NGO St, City",
  city: "New York",
  state: "NY",
  pincode: "10001",
  location: {type: "Point", coordinates: [-73.935242, 40.730610]},
  description: "Helping underprivileged families",
  website: "https://hopefoundation.org",
  beneficiaries_count: 500,
  is_verified: false,
  verification_document: "url_to_pdf",
  created_at: ISODate("2024-01-01T10:00:00Z"),
  updated_at: ISODate("2024-01-01T10:00:00Z"),
  is_active: true
}
```

#### 4. **feedback** Collection
User feedback and ratings
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  donation_id: ObjectId,
  rating: 5,                       // 1-5 stars
  comment: "Great service!",
  feedback_type: "donation",       // 'donation', 'ngo', 'general'
  created_at: ISODate("2024-01-01T10:00:00Z")
}
```

---

## Part 4: Environment Configuration

### Backend .env File
Located at: `backend/.env`

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=True

# MongoDB Configuration
MONGODB_URI=mongodb+srv://annadan_user:YOUR_PASSWORD@Your_CLUSTER_NAME.xxxxx.mongodb.net/
MONGODB_DB_NAME=annadan_db

# JWT Configuration
JWT_SECRET_KEY=Your_Super_Secret_Key_Min_32_Characters
JWT_ACCESS_TOKEN_EXPIRES=3600

# Optional: Google Maps API
GOOGLE_MAPS_API_KEY=AIzaSy...

# Optional: Email Notifications
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### Important Security Notes
- **NEVER** commit `.env` to Git
- Use `.env.example` as template
- Rotate passwords periodically
- Use environment-specific configurations

---

## Part 5: MongoDB Best Practices

### Indexing Strategy
All essential fields are auto-indexed:
- ✓ `email` (unique) - for fast user lookups
- ✓ `donor_id` (standard) - for donor queries
- ✓ `status` (standard) - for filtering donations
- ✓ `location` (geospatial) - for location-based search
- ✓ `created_at` (standard) - for time-based queries

### Query Optimization
```javascript
// Good: Uses index
db.donations.find({status: "available", donor_id: ObjectId("...")})

// Good: Uses geospatial index
db.donations.find({
  location: {
    $near: {
      $geometry: {type: "Point", coordinates: [-73.935242, 40.730610]},
      $maxDistance: 5000  // 5km radius
    }
  }
})

// Avoid: Full collection scan
db.donations.find({description: "rice"})  // No index, slow!
```

### Backup Strategy
Using MongoDB Atlas:
1. Automatic backups every 6 hours
2. 30-day retention in free tier
3. Download backups from Compass: **Deployment → Backups**

### Monitoring
In MongoDB Compass:
1. Open database
2. Go to **Performance Advisor** tab
3. Check for slow queries
4. Optimize indexes if needed

---

## Part 6: Common MongoDB Operations in Compass

### View Collections
1. Click database name → Collections tab
2. See all collections and documents count

### Create Index
1. Right-click collection → Index → Create Index
2. Select fields and options
3. Example: `{email: 1}` for ascending order

### Query Data
1. Click collection
2. Open **Aggregation** or **Filter** tab
3. Write MongoDB query:
   ```javascript
   {status: "available", "location.coordinates": {$exists: true}}
   ```

### Insert Document
1. Click collection → **Insert Document** button
2. Enter JSON data
3. Click **Insert**

### Update Document
1. Right-click document → **Update**
2. Modify the JSON
3. Click **Update**

### Export Data
1. Right-click collection → **Export**
2. Choose format (JSON/CSV)
3. Select fields and download

---

## Part 7: Troubleshooting

### Connection Issues
```
❌ Error: "connect ECONNREFUSED"
✓ Solution: Check MongoDB Atlas cluster is running and IP whitelisted
```

```
❌ Error: "Authentication failed"
✓ Solution: Verify username/password in connection string
```

```
❌ Error: "connection timeout"
✓ Solution: 
  - Check internet connection
  - Verify IP address is whitelisted
  - Increase timeout in connection options
```

### Database Issues
```
❌ Collections not created automatically
✓ Solution: Run collection setup in app/__init__.py on first run
```

```
❌ Duplicate key error
✓ Solution: Email/Phone already exists, use different unique values
```

---

## Part 8: Production Checklist

Before deploying to production:

- [ ] Use paid MongoDB Atlas cluster (M2 or higher)
- [ ] Enable encryption at rest
- [ ] Use VPC Peering for secure connection
- [ ] Enable IP whitelist (specific IPs only)
- [ ] Set up automated backups
- [ ] Enable backup snapshots (daily)
- [ ] Configure database read replicas
- [ ] Set up monitoring and alerts
- [ ] Use strong passwords (32+ chars)
- [ ] Enable SSL/TLS encryption
- [ ] Create separate prod and dev databases
- [ ] Set up database user roles (read-only for app)

---

## Useful Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [MongoDB Compass Guide](https://docs.mongodb.com/compass/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [MongoDB Query Language](https://docs.mongodb.com/manual/reference/operator/query/)
- [Geospatial Queries](https://docs.mongodb.com/manual/geospatial-queries/)

---

**Last Updated:** January 2024
**Status:** ✓ Complete
