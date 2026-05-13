from datetime import datetime
from app.utils.time import utc_now

try:
    from bson import ObjectId
except Exception:
    class ObjectId(str):
        pass


class Feedback:
    """Feedback and Rating model"""

    def __init__(self, db):
        self.db = db
        self.collection = db.feedback
        self.create_indexes()

    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('donation_id')
        self.collection.create_index('from_user_id')
        self.collection.create_index('to_user_id')
        self.collection.create_index('created_at')

    def create_feedback(self, feedback_data):
        """Create new feedback"""
        try:
            feedback_data['created_at'] = utc_now()
            result = self.collection.insert_one(feedback_data)
            return {'success': True, 'feedback_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def find_by_donation(self, donation_id):
        """Find all feedback for a donation"""
        try:
            return list(self.collection.find({'donation_id': donation_id}))
        except Exception:
            return []

    def find_for_user(self, user_id):
        """Find all feedback received by user"""
        try:
            return list(self.collection.find({'to_user_id': user_id}))
        except Exception:
            return []

    def get_user_rating(self, user_id):
        """Calculate average rating for a user"""
        try:
            feedback_list = self.find_for_user(user_id)

            if not feedback_list:
                return {
                    'average_rating': 0,
                    'total_reviews': 0,
                    'rating_breakdown': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                }

            ratings = [int(f.get('rating', 0) or 0) for f in feedback_list]
            avg_rating = sum(ratings) / len(ratings)

            rating_breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for rating in ratings:
                if rating in rating_breakdown:
                    rating_breakdown[rating] += 1

            return {
                'average_rating': round(avg_rating, 2),
                'total_reviews': len(feedback_list),
                'rating_breakdown': rating_breakdown,
            }
        except Exception as e:
            return {'error': str(e)}

    def get_all_feedback(self, skip=0, limit=10):
        """Get all feedback"""
        return list(self.collection.find({}).skip(skip).limit(limit))
