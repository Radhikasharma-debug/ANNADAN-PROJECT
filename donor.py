from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename
from datetime import datetime

from app.models import Donation, Notification
from app.utils import get_current_user, token_required, validate_coordinates
from app.utils.http import get_json_data, parse_pagination
from app.utils.image_upload import ImageUploadService

donor_bp = Blueprint('donor', __name__)


@donor_bp.route('/post-food', methods=['POST'])
@token_required
def post_food():
    """Donor posts available food."""
    try:
        current_user = get_current_user()

        if current_user['user_type'] != 'donor':
            return jsonify({'error': 'Only donors can post food'}), 403

        data = get_json_data(required=True)

        required_fields = ['food_type', 'quantity', 'pickup_time', 'latitude', 'longitude', 'address']
        if not all(field in data and data.get(field) not in (None, '') for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        valid_coords, coords = validate_coordinates(data['latitude'], data['longitude'])
        if not valid_coords:
            return jsonify({'error': coords}), 400

        donation_model = Donation(current_app.db)

        donation_data = {
            'donor_id': current_user['user_id'],
            'food_type': str(data['food_type']).strip(),
            'quantity': data['quantity'],
            'unit': data.get('unit', 'kg'),
            'description': str(data.get('description', '')).strip(),
            'pickup_time': data['pickup_time'],
            'expiry_time': data.get('expiry_time'),
            'location': {
                'address': str(data['address']).strip(),
                'city': str(data.get('city', '')).strip(),
                'coordinates': [float(data['longitude']), float(data['latitude'])],
            },
            'donor_name': str(data.get('donor_name', '')).strip(),
            'donor_phone': str(data.get('donor_phone', '')).strip(),
        }

        result = donation_model.create_donation(donation_data)
        if result.get('success'):
            donation_model.find_nearby(float(data['latitude']), float(data['longitude']))
            return jsonify({'message': 'Food posted successfully', 'donation_id': result['donation_id']}), 201

        return jsonify({'error': result.get('error', 'Failed to create donation')}), 400

    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception:
        current_app.logger.exception('Post food failed')
        return jsonify({'error': 'Failed to post food'}), 500


@donor_bp.route('/my-donations', methods=['GET'])
@token_required
def get_my_donations():
    """Get donor's donations."""
    try:
        current_user = get_current_user()

        if current_user['user_type'] != 'donor':
            return jsonify({'error': 'Unauthorized'}), 403

        skip, limit = parse_pagination(default_limit=50, max_limit=200)

        donation_model = Donation(current_app.db)
        donations = donation_model.find_by_donor(current_user['user_id'], skip=skip, limit=limit)

        for donation in donations:
            donation['_id'] = str(donation['_id'])
            if donation.get('donor_id'):
                donation['donor_id'] = str(donation['donor_id'])
            if donation.get('accepted_by'):
                donation['accepted_by'] = str(donation['accepted_by'])

        return jsonify({'donations': donations, 'total': len(donations)}), 200

    except Exception:
        current_app.logger.exception('Get donor donations failed')
        return jsonify({'error': 'Failed to fetch donations'}), 500


@donor_bp.route('/donation/<donation_id>', methods=['GET'])
def get_donation_detail(donation_id):
    """Get donation details."""
    try:
        donation_model = Donation(current_app.db)
        donation = donation_model.find_by_id(donation_id)

        if not donation:
            return jsonify({'error': 'Donation not found'}), 404

        donation['_id'] = str(donation['_id'])
        if donation.get('donor_id'):
            donation['donor_id'] = str(donation['donor_id'])
        if donation.get('accepted_by'):
            donation['accepted_by'] = str(donation['accepted_by'])

        return jsonify(donation), 200

    except Exception:
        current_app.logger.exception('Get donation detail failed')
        return jsonify({'error': 'Failed to fetch donation'}), 500


@donor_bp.route('/donation/<donation_id>/upload-image', methods=['POST'])
@token_required
def upload_donation_image(donation_id):
    """Upload image for donation."""
    try:
        current_user = get_current_user()
        donation_model = Donation(current_app.db)
        
        # Verify donation exists and belongs to user
        donation = donation_model.find_by_id(donation_id)
        if not donation:
            return jsonify({'error': 'Donation not found'}), 404
        
        if str(donation['donor_id']) != current_user['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if file was provided
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        validation = ImageUploadService.validate_image(file)
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 400
        
        # Save image as base64
        file.seek(0)
        image_result = ImageUploadService.save_image_base64(file)
        
        if not image_result['success']:
            return jsonify({'error': image_result['error']}), 400
        
        # Add image to donation
        image_data = {
            'filename': secure_filename(file.filename),
            'data': image_result['data'],
            'size': image_result['size'],
            'url': None  # Base64 embedded, no separate URL
        }
        
        db_result = donation_model.add_image(donation_id, image_data)
        
        if db_result['success']:
            return jsonify({
                'message': 'Image uploaded successfully',
                'donation_id': donation_id,
                'total_images': len(donation.get('images', [])) + 1
            }), 201
        
        return jsonify({'error': 'Failed to save image'}), 400
    
    except Exception as e:
        current_app.logger.exception('Image upload failed')
        return jsonify({'error': 'Failed to upload image', 'details': str(e)}), 500


@donor_bp.route('/donation/<donation_id>/images', methods=['GET'])
def get_donation_images(donation_id):
    """Get all images for a donation."""
    try:
        donation_model = Donation(current_app.db)
        donation = donation_model.find_by_id(donation_id)
        
        if not donation:
            return jsonify({'error': 'Donation not found'}), 404
        
        images = donation.get('images', [])
        
        # Clean up sensitive data
        for img in images:
            img.pop('data', None)  # Don't send full base64 in list endpoint
        
        return jsonify({
            'donation_id': donation_id,
            'images': images,
            'total': len(images)
        }), 200
    
    except Exception:
        current_app.logger.exception('Get images failed')
        return jsonify({'error': 'Failed to fetch images'}), 500


@donor_bp.route('/donation/<donation_id>/image/<int:image_index>', methods=['DELETE'])
@token_required
def delete_donation_image(donation_id, image_index):
    """Delete image from donation."""
    try:
        current_user = get_current_user()
        donation_model = Donation(current_app.db)
        
        # Verify donation exists and belongs to user
        donation = donation_model.find_by_id(donation_id)
        if not donation:
            return jsonify({'error': 'Donation not found'}), 404
        
        if str(donation['donor_id']) != current_user['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete image
        result = donation_model.delete_image(donation_id, image_index)
        
        if result['success']:
            return jsonify({'message': 'Image deleted successfully'}), 200
        
        return jsonify({'error': result.get('error', 'Failed to delete image')}), 400
    
    except Exception:
        current_app.logger.exception('Delete image failed')
        return jsonify({'error': 'Failed to delete image'}), 500


@donor_bp.route('/donation/<donation_id>', methods=['PUT'])
@token_required
def update_donation(donation_id):
    """Update donation (before acceptance)."""
    try:
        current_user = get_current_user()
        donation_model = Donation(current_app.db)
        donation = donation_model.find_by_id(donation_id)

        if not donation:
            return jsonify({'error': 'Donation not found'}), 404

        if str(donation['donor_id']) != current_user['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403

        if donation['status'] != 'available':
            return jsonify({'error': 'Cannot update accepted donation'}), 400

        data = get_json_data(required=True)
        update_data = {k: v for k, v in data.items() if k not in ['_id', 'donor_id']}

        result = donation_model.update_donation(donation_id, update_data)

        if result.get('success'):
            return jsonify({'message': 'Donation updated successfully'}), 200

        return jsonify({'error': result.get('error', 'Failed to update donation')}), 400

    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception:
        current_app.logger.exception('Update donation failed')
        return jsonify({'error': 'Failed to update donation'}), 500


@donor_bp.route('/donation/<donation_id>/cancel', methods=['POST'])
@token_required
def cancel_donation(donation_id):
    """Cancel donation."""
    try:
        current_user = get_current_user()
        donation_model = Donation(current_app.db)
        donation = donation_model.find_by_id(donation_id)

        if not donation:
            return jsonify({'error': 'Donation not found'}), 404

        if str(donation['donor_id']) != current_user['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403

        if donation['status'] == 'completed':
            return jsonify({'error': 'Cannot cancel completed donation'}), 400

        donation_model.update_status(donation_id, 'cancelled')

        return jsonify({'message': 'Donation cancelled successfully'}), 200

    except Exception:
        current_app.logger.exception('Cancel donation failed')
        return jsonify({'error': 'Failed to cancel donation'}), 500


@donor_bp.route('/donation/<donation_id>/timer/status', methods=['GET'])
def get_pickup_timer_status(donation_id):
    """Get pickup timer status for donation."""
    try:
        donation_model = Donation(current_app.db)
        timer_status = donation_model.get_timer_status(donation_id)
        
        if not timer_status['success']:
            return jsonify({'error': timer_status.get('error', 'Failed to get timer')}), 400
        
        return jsonify(timer_status), 200
    
    except Exception:
        current_app.logger.exception('Get timer status failed')
        return jsonify({'error': 'Failed to get timer status'}), 500


@donor_bp.route('/donation/<donation_id>/timer/set', methods=['POST'])
@token_required
def set_pickup_timer(donation_id):
    """Set pickup deadline timer for donation."""
    try:
        current_user = get_current_user()
        donation_model = Donation(current_app.db)
        
        # Verify donation exists and belongs to user
        donation = donation_model.find_by_id(donation_id)
        if not donation:
            return jsonify({'error': 'Donation not found'}), 404
        
        if str(donation['donor_id']) != current_user['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get pickup time
        data = get_json_data(required=True)
        pickup_time = data.get('pickup_time')
        
        if not pickup_time:
            return jsonify({'error': 'Pickup time required'}), 400
        
        # Set timer
        result = donation_model.set_pickup_deadline(donation_id, pickup_time)
        
        if result['success']:
            timer_status = donation_model.get_timer_status(donation_id)
            return jsonify({
                'message': 'Timer set successfully',
                'timer': timer_status
            }), 200
        
        return jsonify({'error': result.get('error', 'Failed to set timer')}), 400
    
    except Exception:
        current_app.logger.exception('Set timer failed')
        return jsonify({'error': 'Failed to set timer'}), 500


@donor_bp.route('/donations/timers/expired', methods=['GET'])
@token_required
def get_expired_timers():
    """Get all donations with expired timers."""
    try:
        current_user = get_current_user()
        
        # Only donors can view their own expired
        if current_user['user_type'] != 'donor':
            return jsonify({'error': 'Unauthorized'}), 403
        
        donation_model = Donation(current_app.db)
        
        # Get donations with expired timers
        expired_donations = list(
            current_app.db.donations.find({
                'donor_id': current_user['user_id'],
                'timer_expired': True
            }).sort('updated_at', -1)
        )
        
        for donation in expired_donations:
            donation['_id'] = str(donation['_id'])
            if donation.get('donor_id'):
                donation['donor_id'] = str(donation['donor_id'])
        
        return jsonify({
            'expired_timers': expired_donations,
            'total': len(expired_donations)
        }), 200
    
    except Exception:
        current_app.logger.exception('Get expired timers failed')
        return jsonify({'error': 'Failed to fetch expired timers'}), 500
