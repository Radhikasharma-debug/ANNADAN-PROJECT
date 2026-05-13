from datetime import datetime
from app.utils.time import utc_now

try:
    from bson import ObjectId
except Exception:
    class ObjectId(str):
        pass


class NGO:
    """NGO specific model and operations"""

    def __init__(self, db):
        self.db = db
        self.collection = db.ngos
        self.create_indexes()

    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('user_id', unique=True)
        self.collection.create_index('location')
        self.collection.create_index('verified')

    def create_ngo_profile(self, ngo_data):
        """Create NGO profile"""
        try:
            ngo_data['created_at'] = utc_now()
            ngo_data['updated_at'] = utc_now()
            ngo_data['verified'] = False
            ngo_data['total_pickups'] = 0
            ngo_data['rating'] = 0

            result = self.collection.insert_one(ngo_data)
            return {'success': True, 'ngo_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def find_by_user_id(self, user_id):
        """Find NGO profile by user ID"""
        try:
            return self.collection.find_one({'user_id': str(user_id)})
        except Exception:
            return None

    def find_by_id(self, ngo_id):
        """Find NGO by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(ngo_id)})
        except Exception:
            return None

    def find_verified(self, skip=0, limit=10):
        """Find all verified NGOs"""
        return list(self.collection.find({'verified': True}).skip(skip).limit(limit))

    def find_nearby(self, latitude, longitude, radius_km=10):
        """Find nearby NGOs"""
        all_ngos = list(self.collection.find({'verified': True}))
        nearby = []

        for ngo in all_ngos:
            if 'location' in ngo and 'coordinates' in ngo['location']:
                lat = ngo['location']['coordinates'][1]
                lon = ngo['location']['coordinates'][0]

                from app.models.donation import Donation

                distance = Donation.calculate_distance(latitude, longitude, lat, lon)

                if distance <= radius_km:
                    ngo['distance'] = distance
                    nearby.append(ngo)

        return sorted(nearby, key=lambda x: x.get('distance', float('inf')))

    def verify_ngo(self, ngo_id):
        """Verify NGO (admin function)"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(ngo_id)},
                {'$set': {'verified': True, 'updated_at': utc_now()}},
            )
            return {'success': result.modified_count > 0, 'modified_count': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_profile(self, ngo_id, update_data):
        """Update NGO profile"""
        try:
            update_data['updated_at'] = utc_now()
            result = self.collection.update_one({'_id': ObjectId(ngo_id)}, {'$set': update_data})
            return {'success': True, 'modified_count': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def increment_pickups(self, ngo_id):
        """Increment pickup count"""
        try:
            result = self.collection.update_one({'_id': ObjectId(ngo_id)}, {'$inc': {'total_pickups': 1}})
            return {'success': result.modified_count > 0, 'modified_count': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_all_ngos(self, skip=0, limit=10):
        """Get all NGOs with pagination"""
        return list(self.collection.find({}).skip(skip).limit(limit))
