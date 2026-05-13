"""
AI Features API Routes
Endpoints for Smart Matching, Demand Prediction, Chatbot, and Route Optimization
"""

from flask import Blueprint, current_app, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.ai.chatbot import ChatbotManager
from app.ai.demand_prediction import DemandPredictor
from app.ai.matching import DonorNGOMatcher
from app.ai.route_optimization import RouteOptimizer
from app.utils import rate_limit

try:
    from bson import ObjectId
except Exception:
    class ObjectId(str):
        pass


ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Global AI managers (initialized once, refreshed when app/db changes)
_ai_managers = {
    'matcher': None,
    'predictor': None,
    'chatbot': None,
    'router': None,
    'db_ref': None,
    'initialized': False,
}


def _json_body(required=False):
    data = request.get_json(silent=True)
    if data is None:
        if required:
            raise ValueError('Request body must be valid JSON')
        return {}
    if not isinstance(data, dict):
        raise ValueError('Request body must be a JSON object')
    return data


def _safe_object_id(value, field_name='id'):
    try:
        return ObjectId(value)
    except Exception as exc:
        raise ValueError(f'Invalid {field_name}') from exc


def init_ai_routes(app):
    """Initialize AI route handlers with database."""
    if _ai_managers.get('initialized'):
        return ai_bp

    _ai_managers['initialized'] = True

    @ai_bp.before_request
    def setup_ai_managers():
        """Setup AI managers with database connection."""
        db = current_app.db
        if _ai_managers.get('db_ref') is not db:
            _ai_managers['matcher'] = DonorNGOMatcher(db)
            _ai_managers['predictor'] = DemandPredictor(db)
            _ai_managers['chatbot'] = ChatbotManager(db)
            _ai_managers['router'] = RouteOptimizer(db)
            _ai_managers['db_ref'] = db

        g.matcher = _ai_managers['matcher']
        g.predictor = _ai_managers['predictor']
        g.chatbot = _ai_managers['chatbot']
        g.router = _ai_managers['router']

    # ============ SMART DONOR-NGO MATCHING ============

    @ai_bp.route('/matching/find-ngos/<donation_id>', methods=['GET'])
    @rate_limit(40, 60)
    @jwt_required()
    def find_matching_ngos(donation_id):
        """Find best NGOs for a specific donation."""
        try:
            top_k = request.args.get('top_k', 5, type=int)
            donation_obj_id = _safe_object_id(donation_id, field_name='donation_id')

            result = g.matcher.match_donor_to_ngos(donation_id=donation_obj_id, top_k=top_k)

            return jsonify(result), 200 if result.get('success') else 400

        except ValueError as exc:
            return jsonify({'success': False, 'error': str(exc)}), 400
        except Exception:
            current_app.logger.exception('AI matching/find-ngos failed')
            return jsonify({'success': False, 'error': 'Failed to find matching NGOs'}), 500

    @ai_bp.route('/matching/find-donations/<ngo_id>', methods=['GET'])
    @rate_limit(40, 60)
    @jwt_required()
    def find_matching_donations(ngo_id):
        """Find available donations for an NGO."""
        try:
            filters = request.args.to_dict()
            ngo_obj_id = _safe_object_id(ngo_id, field_name='ngo_id')

            result = g.matcher.match_ngo_to_donors(ngo_id=ngo_obj_id, filters=filters)

            return jsonify(result), 200 if result.get('success') else 400

        except ValueError as exc:
            return jsonify({'success': False, 'error': str(exc)}), 400
        except Exception:
            current_app.logger.exception('AI matching/find-donations failed')
            return jsonify({'success': False, 'error': 'Failed to find matching donations'}), 500

    @ai_bp.route('/matching/stats', methods=['GET'])
    def get_matching_stats():
        """Get matching system statistics."""
        try:
            stats = g.matcher.get_matching_stats()
            return jsonify(stats), 200
        except Exception:
            current_app.logger.exception('AI matching stats failed')
            return jsonify({'success': False, 'error': 'Failed to fetch matching stats'}), 500

    # ============ DEMAND PREDICTION ============

    @ai_bp.route('/demand/predict', methods=['GET'])
    def predict_demand():
        """Predict food demand for next N days."""
        try:
            ngo_id = request.args.get('ngo_id')
            days_ahead = request.args.get('days_ahead', 7, type=int)
            include_by_type = request.args.get('include_by_type', 'false').lower() == 'true'

            ngo_obj_id = _safe_object_id(ngo_id, field_name='ngo_id') if ngo_id else None

            result = g.predictor.predict_demand(
                ngo_id=ngo_obj_id,
                days_ahead=days_ahead,
                include_by_type=include_by_type,
            )

            return jsonify(result), 200 if result.get('success') else 400

        except ValueError as exc:
            return jsonify({'success': False, 'error': str(exc)}), 400
        except Exception:
            current_app.logger.exception('AI demand prediction failed')
            return jsonify({'success': False, 'error': 'Failed to predict demand'}), 500

    @ai_bp.route('/demand/urgency', methods=['GET'])
    def predict_urgency():
        """Predict urgency levels for upcoming days."""
        try:
            days_ahead = request.args.get('days_ahead', 7, type=int)
            result = g.predictor.predict_urgency_levels(days_ahead=days_ahead)
            return jsonify(result), 200 if result.get('success') else 400

        except Exception:
            current_app.logger.exception('AI demand urgency failed')
            return jsonify({'success': False, 'error': 'Failed to predict urgency'}), 500

    @ai_bp.route('/demand/critical-periods', methods=['GET'])
    def get_critical_periods():
        """Get periods needing most attention."""
        try:
            result = g.predictor.predict_critical_periods()
            return jsonify(result), 200 if result.get('success') else 400

        except Exception:
            current_app.logger.exception('AI critical periods failed')
            return jsonify({'success': False, 'error': 'Failed to fetch critical periods'}), 500

    @ai_bp.route('/demand/accuracy', methods=['GET'])
    def get_prediction_accuracy():
        """Get model accuracy metrics."""
        try:
            lookback_days = request.args.get('lookback_days', 30, type=int)
            result = g.predictor.get_prediction_accuracy(lookback_days=lookback_days)
            return jsonify(result), 200 if result.get('success') else 400

        except Exception:
            current_app.logger.exception('AI prediction accuracy failed')
            return jsonify({'success': False, 'error': 'Failed to fetch prediction accuracy'}), 500

    # ============ AI CHATBOT ============

    @ai_bp.route('/chatbot/start', methods=['POST'])
    @rate_limit(30, 60)
    def start_chatbot():
        """Start a new chatbot conversation."""
        try:
            payload = _json_body(required=False)
            user_id = payload.get('user_id')

            if not user_id:
                try:
                    jwt_identity = get_jwt_identity()
                    if isinstance(jwt_identity, dict):
                        user_id = jwt_identity.get('user_id')
                    else:
                        user_id = jwt_identity
                except Exception:
                    user_id = 'anonymous'

            result = g.chatbot.start_conversation(user_id=user_id or 'anonymous')
            return jsonify(result), 200

        except ValueError as exc:
            return jsonify({'success': False, 'error': str(exc)}), 400
        except Exception:
            current_app.logger.exception('AI chatbot/start failed')
            return jsonify({'success': False, 'error': 'Failed to start chatbot'}), 500

    @ai_bp.route('/chatbot/message', methods=['POST'])
    @rate_limit(60, 60)
    def chatbot_message():
        """Send message to chatbot and get response."""
        try:
            data = _json_body(required=True)
            user_message = data.get('message')
            conversation_id = data.get('conversation_id')
            user_id = data.get('user_id')

            if not user_message:
                return jsonify({'success': False, 'error': 'No message provided'}), 400

            result = g.chatbot.get_response(
                user_message=user_message,
                conversation_id=conversation_id,
                user_id=user_id,
            )

            return jsonify(result), 200 if result.get('success') else 400

        except ValueError as exc:
            return jsonify({'success': False, 'error': str(exc)}), 400
        except Exception:
            current_app.logger.exception('AI chatbot/message failed')
            return jsonify({'success': False, 'error': 'Failed to process chatbot message'}), 500

    @ai_bp.route('/chatbot/history/<conversation_id>', methods=['GET'])
    def get_chat_history(conversation_id):
        """Get conversation history."""
        try:
            result = g.chatbot.get_conversation_history(conversation_id)
            return jsonify(result), 200 if result.get('success') else 400

        except Exception:
            current_app.logger.exception('AI chatbot/history failed')
            return jsonify({'success': False, 'error': 'Failed to fetch chat history'}), 500

    @ai_bp.route('/chatbot/faq', methods=['GET'])
    def get_faq_categories():
        """Get all FAQ categories."""
        try:
            result = g.chatbot.get_faq_categories()
            return jsonify(result), 200

        except Exception:
            current_app.logger.exception('AI chatbot/faq categories failed')
            return jsonify({'success': False, 'error': 'Failed to fetch FAQ categories'}), 500

    @ai_bp.route('/chatbot/faq/<category>', methods=['GET'])
    def get_faq_item(category):
        """Get specific FAQ item."""
        try:
            result = g.chatbot.get_faq_by_category(category)
            return jsonify(result), 200 if result.get('success') else 400

        except Exception:
            current_app.logger.exception('AI chatbot/faq item failed')
            return jsonify({'success': False, 'error': 'Failed to fetch FAQ item'}), 500

    @ai_bp.route('/chatbot/stats', methods=['GET'])
    def get_chatbot_stats():
        """Get chatbot usage statistics."""
        try:
            result = g.chatbot.get_chatbot_stats()
            return jsonify(result), 200

        except Exception:
            current_app.logger.exception('AI chatbot/stats failed')
            return jsonify({'success': False, 'error': 'Failed to fetch chatbot stats'}), 500

    # ============ ROUTE OPTIMIZATION ============

    @ai_bp.route('/routes/optimize', methods=['POST'])
    @rate_limit(20, 60)
    @jwt_required()
    def optimize_route():
        """Optimize delivery route for NGO."""
        try:
            data = _json_body(required=True)
            ngo_id = data.get('ngo_id')
            pickup_locations = data.get('pickup_locations', [])
            delivery_locations = data.get('delivery_locations', [])
            vehicle_capacity = data.get('vehicle_capacity', 100)

            if not ngo_id:
                return jsonify({'success': False, 'error': 'ngo_id required'}), 400

            ngo_obj_id = _safe_object_id(ngo_id, field_name='ngo_id')

            result = g.router.optimize_route(
                ngo_id=ngo_obj_id,
                pickup_locations=pickup_locations,
                delivery_locations=delivery_locations,
                vehicle_capacity=vehicle_capacity,
            )

            return jsonify(result), 200 if result.get('success') else 400

        except ValueError as exc:
            return jsonify({'success': False, 'error': str(exc)}), 400
        except Exception:
            current_app.logger.exception('AI routes/optimize failed')
            return jsonify({'success': False, 'error': 'Failed to optimize route'}), 500

    @ai_bp.route('/routes/optimize-multi', methods=['POST'])
    @rate_limit(20, 60)
    @jwt_required()
    def optimize_multi_vehicle_route():
        """Optimize routes for multiple vehicles."""
        try:
            data = _json_body(required=True)
            ngo_id = data.get('ngo_id')
            locations = data.get('locations', [])
            num_vehicles = data.get('num_vehicles', 2)
            vehicle_capacity = data.get('vehicle_capacity', 100)

            if not ngo_id:
                return jsonify({'success': False, 'error': 'ngo_id required'}), 400

            ngo_obj_id = _safe_object_id(ngo_id, field_name='ngo_id')

            result = g.router.optimize_multi_vehicle_route(
                ngo_id=ngo_obj_id,
                locations=locations,
                num_vehicles=num_vehicles,
                vehicle_capacity=vehicle_capacity,
            )

            return jsonify(result), 200 if result.get('success') else 400

        except ValueError as exc:
            return jsonify({'success': False, 'error': str(exc)}), 400
        except Exception:
            current_app.logger.exception('AI routes/optimize-multi failed')
            return jsonify({'success': False, 'error': 'Failed to optimize multi-vehicle route'}), 500

    @ai_bp.route('/routes/tracking/<delivery_id>', methods=['GET'])
    @jwt_required()
    def realtime_tracking(delivery_id):
        """Get realtime delivery tracking."""
        try:
            result = g.router.get_realtime_tracking(delivery_id)
            return jsonify(result), 200 if result.get('success') else 400

        except Exception:
            current_app.logger.exception('AI routes/tracking failed')
            return jsonify({'success': False, 'error': 'Failed to fetch tracking data'}), 500

    @ai_bp.route('/routes/consolidation/<ngo_id>', methods=['GET'])
    @jwt_required()
    def suggest_consolidation(ngo_id):
        """Get consolidation suggestions."""
        try:
            ngo_obj_id = _safe_object_id(ngo_id, field_name='ngo_id')
            result = g.router.suggest_consolidation(ngo_id=ngo_obj_id)
            return jsonify(result), 200 if result.get('success') else 400

        except ValueError as exc:
            return jsonify({'success': False, 'error': str(exc)}), 400
        except Exception:
            current_app.logger.exception('AI routes/consolidation failed')
            return jsonify({'success': False, 'error': 'Failed to fetch consolidation suggestions'}), 500

    @ai_bp.route('/routes/stats/<ngo_id>', methods=['GET'])
    @jwt_required()
    def get_route_stats(ngo_id):
        """Get route optimization statistics."""
        try:
            result = g.router.get_optimization_stats(ngo_id)
            return jsonify(result), 200 if result.get('success') else 400

        except Exception:
            current_app.logger.exception('AI routes/stats failed')
            return jsonify({'success': False, 'error': 'Failed to fetch route stats'}), 500

    return ai_bp
