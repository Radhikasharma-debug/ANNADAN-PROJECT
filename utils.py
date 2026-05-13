"""
AI Utilities - Common functions for all AI features
"""

import numpy as np
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
from app.utils.time import ensure_utc, utc_now
import json

class LocationUtils:
    """Location-based calculations"""
    
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in kilometers"""
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def get_location_from_address(address):
        """Mock geocoding - in production use Google Maps API"""
        # This is a simplified mock - implement with actual geolocation service
        coords_map = {
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.7041, 77.1025),
            'bangalore': (12.9716, 77.5946),
            'hyderabad': (17.3850, 78.4867),
        }
        
        addr_lower = address.lower()
        for city, coords in coords_map.items():
            if city in addr_lower:
                return coords
        
        # Return default coordinates
        return (19.0760, 72.8777)
    
    @staticmethod
    def nearby_locations(lat, lon, radius_km=5):
        """Find locations within radius"""
        # Generate sample nearby locations
        return [
            {
                'name': f'Location {i}',
                'lat': lat + np.random.uniform(-0.05, 0.05),
                'lon': lon + np.random.uniform(-0.05, 0.05),
                'distance': np.random.uniform(0.5, radius_km)
            }
            for i in range(3)
        ]


class DataPreprocessor:
    """Data preprocessing for ML models"""
    
    @staticmethod
    def normalize_features(data, features):
        """Normalize numerical features"""
        normalized = data.copy()
        
        for feature in features:
            if feature in data:
                values = [float(v) for v in data[feature]] if isinstance(data[feature], list) else [float(data[feature])]
                if values:
                    min_val = min(values)
                    max_val = max(values)
                    if max_val - min_val != 0:
                        normalized[feature] = (values[0] - min_val) / (max_val - min_val)
        
        return normalized
    
    @staticmethod
    def extract_features(item_data):
        """Extract features for ML models"""
        features = {}
        
        # Basic features
        if 'quantity' in item_data:
            features['quantity'] = float(item_data['quantity'])
        
        if 'perishability' in item_data:
            perishability_map = {'high': 3, 'medium': 2, 'low': 1}
            features['perishability'] = perishability_map.get(item_data['perishability'], 2)
        
        if 'location' in item_data:
            features['location_hash'] = hash(item_data['location']) % 1000
        
        # Temporal features
        if 'created_at' in item_data:
            try:
                created = datetime.fromisoformat(str(item_data['created_at']).replace('Z', '+00:00'))
                created = ensure_utc(created)
                now = utc_now()
                features['hours_since_creation'] = (now - created).total_seconds() / 3600
            except:
                features['hours_since_creation'] = 0
        
        return features
    
    @staticmethod
    def encode_categorical(value, categories):
        """One-hot encode categorical variables"""
        encoded = {cat: 0 for cat in categories}
        if value in encoded:
            encoded[value] = 1
        return encoded


class SimilarityCalculator:
    """Calculate similarity metrics between entities"""
    
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        if len(vec1) == 0 or len(vec2) == 0:
            return 0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sqrt(sum(a**2 for a in vec1))
        mag2 = sqrt(sum(b**2 for b in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        return dot_product / (mag1 * mag2)
    
    @staticmethod
    def jaccard_similarity(set1, set2):
        """Calculate Jaccard similarity between two sets"""
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0
        
        return intersection / union
    
    @staticmethod
    def euclidean_distance(point1, point2):
        """Calculate Euclidean distance between two points"""
        return sqrt(sum((a - b)**2 for a, b in zip(point1, point2)))


class TimeSeriesUtils:
    """Time series analysis for demand prediction"""
    
    @staticmethod
    def get_time_features(dt):
        """Extract time-based features"""
        return {
            'hour': dt.hour,
            'day_of_week': dt.weekday(),
            'day_of_month': dt.day,
            'month': dt.month,
            'is_weekend': dt.weekday() >= 5
        }
    
    @staticmethod
    def create_lag_features(data, lags=[1, 7, 30]):
        """Create lagged features for time series"""
        features = {}
        
        for lag in lags:
            if lag < len(data):
                features[f'lag_{lag}'] = data[-lag-1] if lag < len(data) else 0
        
        return features
    
    @staticmethod
    def rolling_average(data, window=7):
        """Calculate rolling average"""
        if len(data) < window:
            return data
        
        result = []
        for i in range(len(data) - window + 1):
            avg = sum(data[i:i+window]) / window
            result.append(avg)
        
        return result


class ModelEvaluator:
    """Evaluate ML model performance"""
    
    @staticmethod
    def mean_absolute_error(predictions, actuals):
        """Calculate MAE"""
        if len(predictions) != len(actuals):
            return None
        
        return sum(abs(p - a) for p, a in zip(predictions, actuals)) / len(predictions)
    
    @staticmethod
    def mean_squared_error(predictions, actuals):
        """Calculate MSE"""
        if len(predictions) != len(actuals):
            return None
        
        return sum((p - a)**2 for p, a in zip(predictions, actuals)) / len(predictions)
    
    @staticmethod
    def accuracy_score(predictions, actuals):
        """Calculate accuracy for classification"""
        if len(predictions) != len(actuals):
            return None
        
        correct = sum(1 for p, a in zip(predictions, actuals) if p == a)
        return correct / len(predictions)
