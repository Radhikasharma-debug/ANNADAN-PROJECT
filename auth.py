from flask import Blueprint, current_app, jsonify

from app.models import User
from app.utils import generate_token, rate_limit, validate_email, validate_password, validate_phone
from app.utils.http import get_json_data

auth_bp = Blueprint('auth', __name__)


def _to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


@auth_bp.route('/register', methods=['POST'])
@rate_limit(5, 60)
def register():
    """Register new user (donor or NGO)."""
    try:
        data = get_json_data(required=True)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    try:
        email = str(data.get('email', '')).strip().lower()
        phone = str(data.get('phone', '')).strip()
        password = str(data.get('password', ''))
        user_type = str(data.get('user_type', '')).strip().lower()

        if not email or not password or not phone:
            return jsonify({'error': 'Email, phone, and password are required'}), 400

        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        if not validate_phone(phone):
            return jsonify({'error': 'Invalid phone format'}), 400

        valid_pwd, pwd_msg = validate_password(password)
        if not valid_pwd:
            return jsonify({'error': pwd_msg}), 400

        if user_type not in {'donor', 'ngo'}:
            return jsonify({'error': 'Invalid user type'}), 400

        user_model = User(current_app.db)
        user_data = {
            'email': email,
            'phone': phone,
            'password': password,
            'name': str(data.get('name', '')).strip(),
            'user_type': user_type,
            'address': str(data.get('address', '')).strip(),
            'city': str(data.get('city', '')).strip(),
            'state': str(data.get('state', '')).strip(),
        }

        result = user_model.create_user(user_data)
        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Failed to register user')}), 400

        if user_type == 'ngo':
            from app.models import NGO

            ngo_model = NGO(current_app.db)
            ngo_data = {
                'user_id': result['user_id'],
                'name': str(data.get('name', '')).strip(),
                'organization_name': str(data.get('organization_name', '')).strip(),
                'phone': phone,
                'email': email,
                'location': {
                    'address': str(data.get('address', '')).strip(),
                    'city': str(data.get('city', '')).strip(),
                    'coordinates': [_to_float(data.get('longitude', 0)), _to_float(data.get('latitude', 0))],
                },
            }
            ngo_result = ngo_model.create_ngo_profile(ngo_data)
            if not ngo_result.get('success'):
                return jsonify({'error': ngo_result.get('error', 'Failed to create NGO profile')}), 400

        return jsonify({'message': 'User registered successfully', 'user_id': result['user_id']}), 201

    except Exception:
        current_app.logger.exception('Registration failed')
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit(10, 60)
def login():
    """Login user."""
    try:
        data = get_json_data(required=True)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    try:
        email = str(data.get('email', '')).strip().lower()
        password = str(data.get('password', ''))

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user_model = User(current_app.db)
        user = user_model.find_by_email(email)

        if not user or not User.verify_password(password, user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        if user.get('is_active') is False:
            return jsonify({'error': 'User account is inactive'}), 403

        token = generate_token(user['_id'], user['user_type'])

        return jsonify(
            {
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': str(user['_id']),
                    'email': user['email'],
                    'name': user.get('name', ''),
                    'user_type': user['user_type'],
                },
            }
        ), 200

    except Exception:
        current_app.logger.exception('Login failed')
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify email (placeholder)."""
    return jsonify({'message': 'Email verification endpoint', 'token': token}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user."""
    return jsonify({'message': 'Logout successful'}), 200
