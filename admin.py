from flask import Blueprint, current_app, jsonify, request

from app.models import Donation, NGO, User
from app.utils import admin_required
from app.utils.http import parse_pagination

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """Get admin dashboard with statistics."""
    try:
        donation_model = Donation(current_app.db)
        ngo_model = NGO(current_app.db)
        user_model = User(current_app.db)

        stats = {
            'donations': donation_model.get_stats(),
            'total_users': user_model.collection.count_documents({}),
            'total_ngos': ngo_model.collection.count_documents({}),
            'verified_ngos': ngo_model.collection.count_documents({'verified': True}),
            'pending_ngos': ngo_model.collection.count_documents({'verified': False}),
        }

        return jsonify(stats), 200

    except Exception:
        current_app.logger.exception('Admin dashboard failed')
        return jsonify({'error': 'Failed to load dashboard'}), 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users with pagination."""
    try:
        skip, limit = parse_pagination(default_limit=20, max_limit=200)
        user_type = request.args.get('type')

        user_model = User(current_app.db)

        query = {}
        if user_type:
            query['user_type'] = user_type

        users = list(user_model.collection.find(query, {'password': 0}).skip(skip).limit(limit))

        for user in users:
            user['_id'] = str(user['_id'])

        return jsonify({'users': users, 'total': user_model.collection.count_documents(query)}), 200

    except Exception:
        current_app.logger.exception('Admin users list failed')
        return jsonify({'error': 'Failed to fetch users'}), 500


@admin_bp.route('/ngos/verify/<ngo_user_id>', methods=['POST'])
@admin_required
def verify_ngo(ngo_user_id):
    """Verify NGO by user id."""
    try:
        ngo_model = NGO(current_app.db)
        ngo = ngo_model.find_by_user_id(ngo_user_id)

        if not ngo:
            return jsonify({'error': 'NGO not found'}), 404

        result = ngo_model.verify_ngo(ngo['_id'])
        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Failed to verify NGO')}), 400

        return jsonify({'message': 'NGO verified successfully'}), 200

    except Exception:
        current_app.logger.exception('NGO verification failed')
        return jsonify({'error': 'Failed to verify NGO'}), 500


@admin_bp.route('/donations/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get donation analytics."""
    try:
        donation_model = Donation(current_app.db)
        stats = donation_model.get_stats()

        all_donations = list(donation_model.collection.find({}))

        total_quantity_saved = sum(float(d.get('quantity', 0) or 0) for d in all_donations)
        average_quantity = (total_quantity_saved / len(all_donations)) if all_donations else 0

        food_types = {}
        for donation in all_donations:
            food_type = donation.get('food_type', 'Unknown')
            food_types[food_type] = food_types.get(food_type, 0) + 1

        return jsonify(
            {
                'stats': stats,
                'total_quantity_saved': total_quantity_saved,
                'average_donation_quantity': average_quantity,
                'most_common_food_type': max(food_types, key=food_types.get) if food_types else None,
            }
        ), 200

    except Exception:
        current_app.logger.exception('Donation analytics failed')
        return jsonify({'error': 'Failed to compute analytics'}), 500


@admin_bp.route('/user/<user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate user account."""
    try:
        user_model = User(current_app.db)
        result = user_model.update_user(user_id, {'is_active': False})

        if result.get('success'):
            return jsonify({'message': 'User deactivated successfully'}), 200

        return jsonify({'error': result.get('error', 'Failed to deactivate user')}), 400

    except Exception:
        current_app.logger.exception('User deactivation failed')
        return jsonify({'error': 'Failed to deactivate user'}), 500
