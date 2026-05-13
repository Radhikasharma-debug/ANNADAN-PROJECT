from datetime import datetime, timezone, timedelta
from app.utils.time import utc_now
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # For type checkers, assume ObjectId exists
    from bson import ObjectId  # type: ignore
else:
    try:
        from bson import ObjectId
    except Exception:
        # Fallback minimal ObjectId for environments without bson installed.
        # This preserves string behavior so the rest of the code can run in
        # non-production/editor environments; install pymongo/bson for full functionality.
        class ObjectId(str):
            pass


class Donation:
    """Donation (Food posting) model"""

    def __init__(self, db):
        self.db = db
        self.collection = db.donations
        self.create_indexes()

    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('donor_id')
        self.collection.create_index('status')
        self.collection.create_index('accepted_by')
        self.collection.create_index('location')
        self.collection.create_index('created_at')
        self.collection.create_index([('status', 1), ('created_at', -1)])

    def _run_query(self, query, skip=0, limit=None, sort_field=None, sort_direction=-1):
        """Run query against real Mongo cursor or mock list result."""
        result = self.collection.find(query)
        has_cursor_api = hasattr(result, 'sort')

        if has_cursor_api and sort_field:
            result = result.sort(sort_field, sort_direction)
        if has_cursor_api and hasattr(result, 'skip') and skip:
            result = result.skip(skip)
        if has_cursor_api and hasattr(result, 'limit') and limit is not None:
            result = result.limit(limit)

        docs = list(result)

        # Mock DB returns plain list; apply sort/skip/limit manually.
        if not has_cursor_api:
            if sort_field:
                docs = sorted(
                    docs,
                    key=lambda x: x.get(sort_field) or datetime.min.replace(tzinfo=timezone.utc),
                    reverse=sort_direction == -1,
                )
            if skip:
                docs = docs[skip:]
            if limit is not None:
                docs = docs[:limit]

        return docs

    def create_donation(self, donation_data):
        """Create new food donation"""
        try:
            donation_data['created_at'] = utc_now()
            donation_data['updated_at'] = utc_now()
            donation_data['status'] = 'available'  # available, accepted, collected, completed
            donation_data['accepted_by'] = None
            donation_data['images'] = []  # Initialize empty images array

            result = self.collection.insert_one(donation_data)
            return {'success': True, 'donation_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def add_image(self, donation_id, image_data):
        """Add image to donation"""
        try:
            image_record = {
                'filename': image_data.get('filename'),
                'url': image_data.get('url'),
                'data': image_data.get('data'),  # Base64 encoded if stored
                'size': image_data.get('size'),
                'uploaded_at': utc_now()
            }
            
            result = self.collection.update_one(
                {'_id': ObjectId(donation_id)},
                {
                    '$push': {'images': image_record},
                    '$set': {'updated_at': utc_now()}
                }
            )
            
            return {'success': result.modified_count > 0}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_image(self, donation_id, image_index):
        """Delete image from donation"""
        try:
            donation = self.find_by_id(donation_id)
            if not donation or not donation.get('images'):
                return {'success': False, 'error': 'Image not found'}
            
            if image_index < 0 or image_index >= len(donation['images']):
                return {'success': False, 'error': 'Invalid image index'}
            
            result = self.collection.update_one(
                {'_id': ObjectId(donation_id)},
                {
                    '$unset': {f'images.{image_index}': 1},
                    '$set': {'updated_at': utc_now()}
                }
            )
            
            # Remove null entries
            self.collection.update_one(
                {'_id': ObjectId(donation_id)},
                {'$pull': {'images': None}}
            )
            
            return {'success': result.modified_count > 0}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def find_by_id(self, donation_id):
        """Find donation by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(donation_id)})
        except Exception:
            return None

    def find_by_donor(self, donor_id, skip=0, limit=50):
        """Find donations by donor with latest first"""
        try:
            return self._run_query(
                {'donor_id': donor_id},
                skip=skip,
                limit=limit,
                sort_field='created_at',
                sort_direction=-1,
            )
        except Exception:
            return []

    def find_by_accepted_ngo(self, ngo_user_id, skip=0, limit=50, statuses=None):
        """Find donations accepted by NGO user id."""
        try:
            query = {'accepted_by': ngo_user_id}
            if statuses:
                query['status'] = {'$in': list(statuses)}

            return self._run_query(
                query,
                skip=skip,
                limit=limit,
                sort_field='created_at',
                sort_direction=-1,
            )
        except Exception:
            return []

    def find_available(self, skip=0, limit=10):
        """Find all available donations"""
        return self._run_query(
            {'status': 'available'},
            skip=skip,
            limit=limit,
            sort_field='created_at',
            sort_direction=-1,
        )

    def find_nearby(self, latitude, longitude, radius_km=5, max_scan=250):
        """Find donations near a location (simple distance calculation)."""
        available = self.find_available(limit=max_scan)
        nearby = []

        for donation in available:
            if 'location' in donation and 'coordinates' in donation['location']:
                lat = donation['location']['coordinates'][1]
                lon = donation['location']['coordinates'][0]

                # Simple distance calculation (Haversine formula approximation)
                distance = self.calculate_distance(latitude, longitude, lat, lon)

                if distance <= radius_km:
                    donation['distance'] = distance
                    nearby.append(donation)

        return sorted(nearby, key=lambda x: x.get('distance', float('inf')))

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in km"""
        from math import radians, cos, sin, asin, sqrt

        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in km
        return c * r

    def accept_donation(self, donation_id, ngo_id):
        """Accept donation as NGO"""
        try:
            result = self.collection.update_one(
                {
                    '_id': ObjectId(donation_id),
                    'status': 'available',
                },
                {
                    '$set': {
                        'status': 'accepted',
                        'accepted_by': ngo_id,  # Store as string, not ObjectId
                        'accepted_at': utc_now(),
                        'updated_at': utc_now(),
                    }
                },
            )
            return {'success': True, 'modified_count': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_donation(self, donation_id, update_data):
        """Update editable donation fields"""
        try:
            safe_update = {k: v for k, v in update_data.items() if k not in {'_id', 'donor_id'}}
            safe_update['updated_at'] = utc_now()

            result = self.collection.update_one(
                {'_id': ObjectId(donation_id)},
                {'$set': safe_update},
            )
            return {'success': True, 'modified_count': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_status(self, donation_id, status):
        """Update donation status"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(donation_id)},
                {'$set': {'status': status, 'updated_at': utc_now()}},
            )
            return {'success': True, 'modified_count': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_stats(self):
        """Get donation statistics"""
        return {
            'total_donations': self.collection.count_documents({}),
            'available': self.collection.count_documents({'status': 'available'}),
            'accepted': self.collection.count_documents({'status': 'accepted'}),
            'completed': self.collection.count_documents({'status': 'completed'}),
        }

    def set_pickup_deadline(self, donation_id, pickup_time):
        """Set pickup deadline/timer for donation"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(donation_id)},
                {
                    '$set': {
                        'pickup_time': pickup_time,
                        'pickup_deadline': pickup_time,
                        'timer_started_at': utc_now(),
                        'timer_active': True,
                        'updated_at': utc_now()
                    }
                }
            )
            return {'success': result.modified_count > 0}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_timer_status(self, donation_id):
        """Get timer status for a donation"""
        try:
            donation = self.find_by_id(donation_id)
            if not donation:
                return {'success': False, 'error': 'Donation not found'}

            now = utc_now()
            pickup_deadline = donation.get('pickup_deadline')

            if not pickup_deadline:
                return {
                    'success': True,
                    'donation_id': donation_id,
                    'timer_active': False,
                    'time_remaining_seconds': 0,
                    'status': 'not_set'
                }

            # Convert to datetime if string
            if isinstance(pickup_deadline, str):
                pickup_deadline = datetime.fromisoformat(pickup_deadline.replace('Z', '+00:00'))

            time_diff = pickup_deadline - now
            time_remaining = int(time_diff.total_seconds())

            status = 'not_set'
            if time_remaining > 0:
                if time_remaining > 3600:  # More than 1 hour
                    status = 'on_track'
                elif time_remaining > 900:  # 15 mins to 1 hour
                    status = 'warning'
                else:  # Less than 15 mins
                    status = 'urgent'
            else:
                status = 'expired'

            return {
                'success': True,
                'donation_id': donation_id,
                'timer_active': donation.get('timer_active', False),
                'pickup_deadline': pickup_deadline.isoformat() if pickup_deadline else None,
                'time_remaining_seconds': max(0, time_remaining),
                'status': status,
                'is_expired': time_remaining <= 0
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def clear_expired_timers(self):
        """Mark donations with expired timers"""
        try:
            now = utc_now()
            result = self.collection.update_many(
                {
                    'pickup_deadline': {'$lt': now},
                    'status': {'$in': ['available', 'accepted']}
                },
                {
                    '$set': {
                        'timer_expired': True,
                        'updated_at': now
                    }
                }
            )
            return {'success': True, 'modified': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}
