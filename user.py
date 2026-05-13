from datetime import datetime
from app.utils.time import utc_now
import os
import importlib
import hashlib
import hmac
import binascii

try:
    from bson import ObjectId
except Exception:
    class ObjectId(str):
        pass


# Try to import bcrypt; if unavailable, use PBKDF2 fallback for non-production contexts.
class _BcryptFallback:
    @staticmethod
    def gensalt():
        return os.urandom(16)

    @staticmethod
    def hashpw(password, salt=None):
        if salt is None:
            salt = _BcryptFallback.gensalt()
        if isinstance(password, str):
            password = password.encode('utf-8')

        dk = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
        return binascii.hexlify(salt + dk)

    @staticmethod
    def checkpw(password, hashed):
        if isinstance(password, str):
            password = password.encode('utf-8')

        hashed_hex = hashed.decode('utf-8') if isinstance(hashed, bytes) else hashed
        all_bytes = binascii.unhexlify(hashed_hex)
        salt = all_bytes[:16]
        stored_dk = all_bytes[16:]
        new_dk = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
        return hmac.compare_digest(new_dk, stored_dk)


try:
    import bcrypt as _bcrypt
except Exception:
    _bcrypt = _BcryptFallback()


# Try to load python-dotenv at runtime; if it's not available, provide a no-op fallback.
try:
    _dotenv = importlib.import_module('dotenv')
    load_dotenv = _dotenv.load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):
        return False


load_dotenv()


class User:
    """User model for both donors and NGOs"""

    def __init__(self, db):
        self.db = db
        self.collection = db.users
        self.create_indexes()

    def create_indexes(self):
        """Create database indexes for optimized queries"""
        self.collection.create_index('email', unique=True)
        self.collection.create_index('phone', unique=True)
        self.collection.create_index('user_type')

    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt (or PBKDF2 fallback)."""
        hashed = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt())
        return hashed.decode('utf-8') if isinstance(hashed, bytes) else str(hashed)

    @staticmethod
    def verify_password(password, hashed):
        """Verify password."""
        hashed_bytes = hashed.encode('utf-8') if isinstance(hashed, str) else hashed
        return _bcrypt.checkpw(password.encode('utf-8'), hashed_bytes)

    def create_user(self, user_data):
        """Create new user"""
        try:
            user_data['password'] = self.hash_password(user_data['password'])
            user_data['created_at'] = utc_now()
            user_data['updated_at'] = utc_now()
            user_data['is_active'] = True

            result = self.collection.insert_one(user_data)
            return {'success': True, 'user_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def find_by_email(self, email):
        """Find user by email"""
        return self.collection.find_one({'email': email})

    def find_by_id(self, user_id):
        """Find user by ID"""
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            return self.collection.find_one({'_id': user_id})
        except Exception:
            return None

    def update_user(self, user_id, update_data):
        """Update user information"""
        try:
            update_data['updated_at'] = utc_now()
            result = self.collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
            return {'success': True, 'modified_count': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_all_users(self, user_type=None):
        """Get all users, optionally filtered by type"""
        query = {}
        if user_type:
            query['user_type'] = user_type
        return list(self.collection.find(query, {'password': 0}))
