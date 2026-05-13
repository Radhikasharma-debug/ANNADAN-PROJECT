"""
Smart Donor-NGO Matching
Uses multiple factors to match donors with suitable NGOs
"""

import numpy as np
from app.ai.utils import LocationUtils, DataPreprocessor, SimilarityCalculator
from app.utils.time import ensure_utc, utc_now

class DonorNGOMatcher:
    """Intelligent matching algorithm for donors and NGOs"""
    
    def __init__(self, db):
        self.db = db
        self.donors_collection = db.users
        self.ngos_collection = db.ngos
        self.donations_collection = db.donations
    
    def match_donor_to_ngos(self, donation_id, top_k=5):
        """
        Find best NGO matches for a donation
        Consider: location, food type, NGO capacity, past performance
        """
        try:
            # Get donation details
            donation = self.donations_collection.find_one({'_id': donation_id})
            if not donation:
                return {'success': False, 'error': 'Donation not found'}
            
            # Get donor info
            donor = self.donors_collection.find_one({'_id': donation.get('donor_id')})
            
            # Get all verified NGOs
            ngos = list(self.ngos_collection.find({'verified': True}))
            
            if not ngos:
                return {'success': False, 'error': 'No verified NGOs found'}
            
            # Calculate match scores
            matches = []
            
            for ngo in ngos:
                score = self._calculate_match_score(
                    donation=donation,
                    donor=donor,
                    ngo=ngo
                )
                
                matches.append({
                    'ngo_id': str(ngo['_id']),
                    'ngo_name': ngo.get('name', 'Unknown NGO'),
                    'score': score,
                    'location': ngo.get('location'),
                    'rating': ngo.get('rating', 0),
                    'specialty': ngo.get('specialty', 'General'),
                    'capacity': ngo.get('capacity', 0),
                    'distance_km': self._calculate_distance(
                        donation.get('location'),
                        ngo.get('location')
                    )
                })
            
            # Sort by score and return top K
            matches = sorted(matches, key=lambda x: x['score'], reverse=True)
            
            return {
                'success': True,
                'donation_id': str(donation_id),
                'matches': matches[:top_k],
                'total_ngos': len(ngos)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def match_ngo_to_donors(self, ngo_id, filters=None):
        """
        Find available donations suitable for an NGO
        Consider: NGO's specialty, location, capacity
        """
        try:
            # Get NGO details
            ngo = self.ngos_collection.find_one({'_id': ngo_id})
            if not ngo:
                return {'success': False, 'error': 'NGO not found'}
            
            # Get available donations
            query = {'status': 'available'}
            if filters and 'food_type' in filters:
                query['food_type'] = filters['food_type']
            
            donations = list(self.donations_collection.find(query).limit(20))
            
            # Calculate match scores
            matches = []
            
            for donation in donations:
                score = self._calculate_match_score_for_ngo(
                    donation=donation,
                    ngo=ngo
                )
                
                matches.append({
                    'donation_id': str(donation['_id']),
                    'donor_name': donation.get('donor_name', 'Anonymous'),
                    'score': score,
                    'food_type': donation.get('food_type'),
                    'quantity': donation.get('quantity'),
                    'location': donation.get('location'),
                    'urgency': self._calculate_urgency(donation),
                    'perishability': donation.get('perishability', 'medium'),
                    'distance_km': self._calculate_distance(
                        donation.get('location'),
                        ngo.get('location')
                    )
                })
            
            # Sort by score
            matches = sorted(matches, key=lambda x: x['score'], reverse=True)
            
            return {
                'success': True,
                'ngo_id': str(ngo_id),
                'matches': matches,
                'total_available_donations': len(donations)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_match_score(self, donation, donor, ngo):
        """Calculate overall match score (0-100)"""
        scores = {}
        
        # Location proximity (weight: 30%)
        distance = self._calculate_distance(
            donation.get('location'),
            ngo.get('location')
        )
        location_score = max(0, 100 - (distance * 2))  # Penalize distance
        scores['location'] = location_score * 0.30
        
        # NGO specialization match (weight: 25%)
        ngo_specialty = ngo.get('specialty', 'general').lower()
        donation_type = donation.get('food_type', 'general').lower()
        
        specialty_match = 100 if ngo_specialty in donation_type or donation_type in ngo_specialty else 50
        scores['specialty'] = specialty_match * 0.25
        
        # NGO capacity check (weight: 20%)
        ngo_capacity = ngo.get('capacity', 1000)
        donation_qty = float(donation.get('quantity', 0))
        
        capacity_score = 100 if donation_qty <= ngo_capacity else 50
        scores['capacity'] = capacity_score * 0.20
        
        # NGO rating/reliability (weight: 15%)
        ngo_rating = ngo.get('rating', 0) / 5.0 * 100  # Normalize to 100
        scores['reliability'] = ngo_rating * 0.15
        
        # Timing/urgency (weight: 10%)
        urgency = self._calculate_urgency(donation)
        urgency_score = urgency * 100  # Already 0-1
        scores['urgency'] = urgency_score * 0.10
        
        total_score = sum(scores.values())
        return round(total_score, 2)
    
    def _calculate_match_score_for_ngo(self, donation, ngo):
        """Calculate match score for NGO-to-Donor matching"""
        scores = {}
        
        # Distance (weight: 25%)
        distance = self._calculate_distance(
            donation.get('location'),
            ngo.get('location')
        )
        distance_score = max(0, 100 - (distance * 2))
        scores['distance'] = distance_score * 0.25
        
        # Urgency (weight: 25%)
        urgency = self._calculate_urgency(donation)
        scores['urgency'] = urgency * 100 * 0.25
        
        # Perishability (weight: 20%)
        perishability = donation.get('perishability', 'medium').lower()
        perishability_map = {'high': 100, 'medium': 70, 'low': 40}
        perishability_score = perishability_map.get(perishability, 70)
        scores['perishability'] = perishability_score * 0.20
        
        # Capacity (weight: 20%)
        ngo_capacity = ngo.get('capacity', 1000)
        donation_qty = float(donation.get('quantity', 0))
        capacity_score = 100 if donation_qty <= ngo_capacity else 50
        scores['capacity'] = capacity_score * 0.20
        
        # Specialty match (weight: 10%)
        specialty_match = 100 if ngo.get('specialty', '').lower() in donation.get('food_type', '').lower() else 50
        scores['specialty'] = specialty_match * 0.10
        
        total_score = sum(scores.values())
        return round(total_score, 2)
    
    def _calculate_distance(self, loc1, loc2):
        """Calculate distance between two locations in km"""
        if not loc1 or not loc2:
            return 999  # Max distance if missing
        
        lat1, lon1 = loc1.get('latitude', 0), loc1.get('longitude', 0)
        lat2, lon2 = loc2.get('latitude', 0), loc2.get('longitude', 0)
        
        return LocationUtils.haversine_distance(lat1, lon1, lat2, lon2)
    
    def _calculate_urgency(self, donation):
        """Calculate urgency score (0-1) based on perishability and time"""
        perishability = donation.get('perishability', 'medium').lower()
        perishability_weights = {'high': 0.9, 'medium': 0.5, 'low': 0.2}
        
        try:
            created_at = donation.get('created_at')
            if created_at:
                normalized_created = ensure_utc(created_at)
                hours_ago = (utc_now() - normalized_created).total_seconds() / 3600
                # Increase urgency over time
                time_factor = min(1.0, hours_ago / 24)  # Max after 24 hours
            else:
                time_factor = 0.5
        except:
            time_factor = 0.5
        
        urgency = (perishability_weights.get(perishability, 0.5) + time_factor) / 2
        return min(1.0, urgency)
    
    def get_matching_stats(self):
        """Get statistics on matching success"""
        try:
            total_donations = self.donations_collection.count_documents({})
            matched_donations = self.donations_collection.count_documents({'status': {'$in': ['accepted', 'completed']}})
            
            return {
                'total_donations': total_donations,
                'matched_donations': matched_donations,
                'success_rate': (matched_donations / total_donations * 100) if total_donations > 0 else 0,
                'avg_match_time_hours': self._calculate_avg_match_time()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_avg_match_time(self):
        """Calculate average time from posting to accepting"""
        try:
            pipeline = [
                {
                    '$match': {'status': 'completed'}
                },
                {
                    '$group': {
                        '_id': None,
                        'avg_time': {
                            '$avg': {
                                '$subtract': ['$accepted_at', '$created_at']
                            }
                        }
                    }
                }
            ]
            
            result = list(self.donations_collection.aggregate(pipeline))
            if result and result[0].get('avg_time'):
                return result[0]['avg_time'] / 3600  # Convert to hours
            return 0
        except:
            return 0
