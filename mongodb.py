"""
MongoDB utilities and connection management
Provides connection pooling, reconnection logic, and best practices
"""

from pymongo import MongoClient, errors
from pymongo.errors import (
    ServerSelectionTimeoutError,
    OperationFailure,
    ConnectionFailure
)
from contextlib import contextmanager
from typing import Optional, Generator, Any
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class MongoDBConnection:
    """MongoDB connection manager with helper methods"""
    
    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Any] = None
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.uri: str = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.db_name: str = os.getenv('MONGODB_DB_NAME', 'annadan_db')
        self.connection_options: dict = {
            'serverSelectionTimeoutMS': 5000,
            'connectTimeoutMS': 10000,
            'retryWrites': True,
            'w': 'majority',
            'maxPoolSize': 10,
            'minPoolSize': 5,
        }
    
    def connect(self) -> bool:
        """Establish connection to MongoDB"""
        try:
            if self._client is None:
                logger.info("Establishing MongoDB connection...")
                self._client = MongoClient(self.uri, **self.connection_options)
                
                # Test connection
                self._client.admin.command('ping')
                self._db = self._client[self.db_name]
                
                logger.info(f"✓ Successfully connected to MongoDB: {self.db_name}")
                self._setup_collections()
                return True
            return True
        except ServerSelectionTimeoutError:
            logger.error("✗ MongoDB connection timeout - server not responding")
            return False
        except ConnectionFailure as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected MongoDB error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")
    
    def get_db(self) -> Any:
        """Get database instance"""
        if self._db is None:
            if not self.connect():
                raise RuntimeError("Failed to establish MongoDB connection")
        return self._db
    
    def _setup_collections(self) -> None:
        """Initialize collections with indexes and schema validation"""
        if self._db is None:
            logger.error("Database not initialized")
            return
            
        db = self._db
        
        # Users collection
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
            db.users.create_index('email', unique=True)
            db.users.create_index('phone', sparse=True)
            db.users.create_index('created_at')
            logger.info("Created 'users' collection with indexes")
        
        # Donations collection
        if 'donations' not in db.list_collection_names():
            db.create_collection('donations')
            db.donations.create_index('donor_id')
            db.donations.create_index('status')
            db.donations.create_index('location')
            db.donations.create_index('created_at')
            logger.info("Created 'donations' collection with indexes")
        
        # NGOs collection
        if 'ngos' not in db.list_collection_names():
            db.create_collection('ngos')
            db.ngos.create_index('email', unique=True)
            db.ngos.create_index('created_at')
            logger.info("Created 'ngos' collection with indexes")
        
        # Feedback collection
        if 'feedback' not in db.list_collection_names():
            db.create_collection('feedback')
            db.feedback.create_index('user_id')
            db.feedback.create_index('created_at')
            logger.info("Created 'feedback' collection with indexes")
    
    def health_check(self) -> bool:
        """Check MongoDB connection health"""
        try:
            if self._client:
                self._client.admin.command('ping')
                return True
        except Exception as e:
            logger.warning(f"MongoDB health check failed: {e}")
            self.disconnect()
            return False
        return False
    
    @contextmanager
    def session(self) -> Generator[Any, None, None]:
        """Context manager for database operations"""
        if self._client is None:
            raise RuntimeError("MongoDB client not initialized. Call connect() first.")
        session = self._client.start_session()
        try:
            yield session
        finally:
            session.end_session()


# Singleton instance
_mongo: Optional[MongoDBConnection] = None

def get_mongodb() -> MongoDBConnection:
    """Get MongoDB connection singleton"""
    global _mongo
    if _mongo is None:
        _mongo = MongoDBConnection()
        _mongo.connect()
    return _mongo


def init_mongodb(app: Any) -> MongoDBConnection:
    """Initialize MongoDB with Flask app"""
    mongo = get_mongodb()
    app.db = mongo.get_db()  # type: ignore
    
    @app.before_request
    def before_request() -> None:
        # Health check on each request
        if not mongo.health_check():
            logger.warning("MongoDB reconnecting...")
            mongo.disconnect()
            mongo.connect()
    
    @app.teardown_appcontext
    def shutdown_session(exception: Optional[Exception] = None) -> None:
        # Execute cleanup
        pass
    
    return mongo
