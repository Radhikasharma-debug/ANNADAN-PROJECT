from flask import Blueprint, current_app, jsonify
from app.models import Donation, NGO, User
from app.utils import get_current_user, token_required
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/donor-stats', methods=['GET'])
@token_required
def get_donor_stats():
    """Get comprehensive donor dashboard statistics"""
    try:
        current_user = get_current_user()
        
        if current_user['user_type'] != 'donor':
            return jsonify({'error': 'Only donors can access this'}), 403
        
        donor_id = current_user['user_id']
        donation_model = Donation(current_app.db)
        
        # Get all donations by this donor
        all_donations = donation_model.find_by_donor(donor_id, skip=0, limit=10000)
        
        # Calculate stats
        total_donations = len(all_donations)
        
        # Calculate total quantity (in kg)
        total_meals_saved = sum(
            float(d.get('quantity', 0)) for d in all_donations
        )
        
        # Count by status
        status_counts = {
            'available': 0,
            'accepted': 0,
            'collected': 0,
            'completed': 0
        }
        
        for donation in all_donations:
            status = donation.get('status', 'available')
            if status in status_counts:
                status_counts[status] += 1
        
        # Get recent donations (last 5)
        recent_donations = all_donations[:5]
        for donation in recent_donations:
            donation['_id'] = str(donation['_id'])
            donation['donor_id'] = str(donation['donor_id'])
        
        # Calculate people potentially helped (assuming ~1 meal per 0.5kg)
        people_helped = int(total_meals_saved * 2)
        
        # Get this month's donations
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        this_month_donations = [
            d for d in all_donations 
            if datetime.fromisoformat(str(d.get('created_at', '')).replace('Z', '+00:00')) >= month_start
        ] if all_donations else []
        
        return jsonify({
            'success': True,
            'donor_stats': {
                'total_donations': total_donations,
                'total_meals_saved': round(total_meals_saved, 2),
                'people_helped': people_helped,
                'this_month_donations': len(this_month_donations),
                'status_breakdown': status_counts,
                'recent_donations': recent_donations,
                'impact_message': f"🎉 You've saved {total_meals_saved:.1f}kg of food and helped {people_helped} people!"
            }
        }), 200
    
    except Exception as e:
        current_app.logger.exception('Donor stats failed')
        return jsonify({'error': 'Failed to fetch donor statistics', 'details': str(e)}), 500


@dashboard_bp.route('/ngo-stats', methods=['GET'])
@token_required
def get_ngo_stats():
    """Get comprehensive NGO dashboard statistics"""
    try:
        current_user = get_current_user()
        
        if current_user['user_type'] != 'ngo':
            return jsonify({'error': 'Only NGOs can access this'}), 403
        
        user_id = current_user['user_id']
        ngo_model = NGO(current_app.db)
        donation_model = Donation(current_app.db)
        
        # Get NGO profile
        ngo_profile = ngo_model.find_by_user_id(user_id)
        if not ngo_profile:
            return jsonify({'error': 'NGO profile not found'}), 404
        
        # Get all donations accepted by this NGO
        all_accepted = donation_model.find_by_accepted_ngo(user_id, skip=0, limit=10000)
        
        # Calculate stats
        total_pickups = len(all_accepted)
        
        # Calculate total quantity distributed
        total_food_distributed = sum(
            float(d.get('quantity', 0)) for d in all_accepted
        )
        
        # Count by status
        status_counts = {
            'accepted': 0,
            'collected': 0,
            'completed': 0
        }
        
        for donation in all_accepted:
            status = donation.get('status', 'accepted')
            if status in status_counts:
                status_counts[status] += 1
        
        # Get recent pickups (last 5)
        recent_pickups = all_accepted[:5]
        for pickup in recent_pickups:
            pickup['_id'] = str(pickup['_id'])
            pickup['donor_id'] = str(pickup['donor_id'])
        
        # Calculate people served (assuming ~1 meal per 0.5kg)
        people_served = int(total_food_distributed * 2)
        
        # Get active pickups (status = accepted or collected)
        active_pickups = [
            d for d in all_accepted 
            if d.get('status') in ['accepted', 'collected']
        ]
        
        return jsonify({
            'success': True,
            'ngo_stats': {
                'total_pickups': total_pickups,
                'total_food_distributed': round(total_food_distributed, 2),
                'people_served': people_served,
                'active_pickups': len(active_pickups),
                'status_breakdown': status_counts,
                'ngo_name': ngo_profile.get('ngo_name', 'NGO'),
                'recent_pickups': recent_pickups,
                'impact_message': f"🌟 {ngo_profile.get('ngo_name', 'Your NGO')} has distributed {total_food_distributed:.1f}kg to {people_served} people!"
            }
        }), 200
    
    except Exception as e:
        current_app.logger.exception('NGO stats failed')
        return jsonify({'error': 'Failed to fetch NGO statistics', 'details': str(e)}), 500


@dashboard_bp.route('/donation-timeline', methods=['GET'])
@token_required
def get_donation_timeline():
    """Get timeline view of donations for charts/graphs"""
    try:
        current_user = get_current_user()
        donation_model = Donation(current_app.db)
        
        if current_user['user_type'] == 'donor':
            donations = donation_model.find_by_donor(current_user['user_id'], skip=0, limit=10000)
            data_type = 'donations'
        elif current_user['user_type'] == 'ngo':
            donations = donation_model.find_by_accepted_ngo(current_user['user_id'], skip=0, limit=10000)
            data_type = 'pickups'
        else:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Group by date
        timeline = {}
        for donation in donations:
            try:
                created_at = donation.get('created_at')
                if isinstance(created_at, str):
                    date = created_at.split('T')[0]
                else:
                    date = created_at.strftime('%Y-%m-%d') if created_at else 'Unknown'
                
                if date not in timeline:
                    timeline[date] = {'count': 0, 'quantity': 0}
                
                timeline[date]['count'] += 1
                timeline[date]['quantity'] += float(donation.get('quantity', 0))
            except:
                pass
        
        return jsonify({
            'success': True,
            'timeline': timeline,
            'data_type': data_type
        }), 200
    
    except Exception as e:
        current_app.logger.exception('Timeline failed')
        return jsonify({'error': 'Failed to fetch timeline', 'details': str(e)}), 500
