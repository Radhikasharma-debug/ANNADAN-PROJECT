from datetime import datetime, timezone
from app.utils.time import utc_now
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bson import ObjectId
else:
    try:
        from bson import ObjectId
    except Exception:
        class ObjectId(str):
            pass


class Notification:
    """Notification model for user notifications"""

    def __init__(self, db):
        self.db = db
        self.collection = db.notifications
        self.create_indexes()

    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('recipient_id')
        self.collection.create_index('is_read')
        self.collection.create_index('created_at')
        self.collection.create_index([('recipient_id', 1), ('is_read', 1)])
        self.collection.create_index([('recipient_id', 1), ('created_at', -1)])

    def create_notification(self, notification_data):
        """Create a new notification"""
        try:
            notification_data['created_at'] = utc_now()
            notification_data['is_read'] = False
            notification_data['read_at'] = None
            
            result = self.collection.insert_one(notification_data)
            return {'success': True, 'notification_id': str(result.inserted_id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_notifications(self, user_id, skip=0, limit=20, unread_only=False):
        """Get notifications for a user"""
        try:
            query = {'recipient_id': user_id}
            if unread_only:
                query['is_read'] = False
            
            notifications = list(
                self.collection.find(query)
                .sort('created_at', -1)
                .skip(skip)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for notif in notifications:
                notif['_id'] = str(notif['_id'])
                if notif.get('related_user_id'):
                    notif['related_user_id'] = str(notif['related_user_id'])
                if notif.get('donation_id'):
                    notif['donation_id'] = str(notif['donation_id'])
            
            return notifications
        except Exception as e:
            return []

    def get_unread_count(self, user_id):
        """Get count of unread notifications"""
        try:
            count = self.collection.count_documents({
                'recipient_id': user_id,
                'is_read': False
            })
            return count
        except Exception:
            return 0

    def mark_as_read(self, notification_id, user_id):
        """Mark notification as read"""
        try:
            result = self.collection.update_one(
                {
                    '_id': ObjectId(notification_id),
                    'recipient_id': user_id
                },
                {
                    '$set': {
                        'is_read': True,
                        'read_at': utc_now()
                    }
                }
            )
            return {'success': result.modified_count > 0}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def mark_all_as_read(self, user_id):
        """Mark all unread notifications as read"""
        try:
            result = self.collection.update_many(
                {
                    'recipient_id': user_id,
                    'is_read': False
                },
                {
                    '$set': {
                        'is_read': True,
                        'read_at': utc_now()
                    }
                }
            )
            return {'success': True, 'modified': result.modified_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_notification(self, notification_id, user_id):
        """Delete notification"""
        try:
            result = self.collection.delete_one({
                '_id': ObjectId(notification_id),
                'recipient_id': user_id
            })
            return {'success': result.deleted_count > 0}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def find_by_id(self, notification_id):
        """Find notification by ID"""
        try:
            notif = self.collection.find_one({'_id': ObjectId(notification_id)})
            if notif:
                notif['_id'] = str(notif['_id'])
                if notif.get('related_user_id'):
                    notif['related_user_id'] = str(notif['related_user_id'])
                if notif.get('donation_id'):
                    notif['donation_id'] = str(notif['donation_id'])
            return notif
        except Exception:
            return None

    def send_donation_matched_notification(self, ngo_id, donation_id, donor_name):
        """Send notification when donation matched to NGO"""
        notification_data = {
            'recipient_id': ngo_id,
            'type': 'donation_matched',
            'title': '🎉 New Donation Match!',
            'message': f'Donation from {donor_name} matched to your organization',
            'icon': '🎉',
            'donation_id': donation_id,
            'action_url': f'/donation/{donation_id}',
            'action_text': 'View Donation',
            'priority': 'high'
        }
        return self.create_notification(notification_data)

    def send_donation_accepted_notification(self, donor_id, ngo_name):
        """Send notification when donation is accepted by NGO"""
        notification_data = {
            'recipient_id': donor_id,
            'type': 'donation_accepted',
            'title': '✅ Donation Accepted!',
            'message': f'Your donation has been accepted by {ngo_name}',
            'icon': '✅',
            'action_url': '/dashboard',
            'action_text': 'View Status',
            'priority': 'high'
        }
        return self.create_notification(notification_data)

    def send_pickup_reminder_notification(self, donor_id, ngo_name, donation_id):
        """Send pickup reminder notification"""
        notification_data = {
            'recipient_id': donor_id,
            'type': 'pickup_reminder',
            'title': '⏰ Pickup Reminder',
            'message': f'{ngo_name} is coming to pick up your donation soon',
            'icon': '⏰',
            'donation_id': donation_id,
            'action_url': f'/donation/{donation_id}',
            'action_text': 'View Details',
            'priority': 'medium'
        }
        return self.create_notification(notification_data)

    def send_donation_collected_notification(self, donor_id, ngo_name, quantity):
        """Send notification when donation is collected"""
        notification_data = {
            'recipient_id': donor_id,
            'type': 'donation_collected',
            'title': '🙏 Thank You!',
            'message': f'{ngo_name} collected {quantity} kg of your donation',
            'icon': '🙏',
            'action_url': '/dashboard',
            'action_text': 'View Impact',
            'priority': 'medium'
        }
        return self.create_notification(notification_data)

    def send_ngo_interested_notification(self, donor_id, ngo_name, donation_id):
        """Send notification when NGO expresses interest"""
        notification_data = {
            'recipient_id': donor_id,
            'type': 'ngo_interested',
            'title': '👀 Interest Alert',
            'message': f'{ngo_name} is interested in your donation',
            'icon': '👀',
            'donation_id': donation_id,
            'action_url': f'/donation/{donation_id}',
            'action_text': 'Review Request',
            'priority': 'high'
        }
        return self.create_notification(notification_data)

    def clear_old_notifications(self, days=90):
        """Clear read notifications older than specified days"""
        try:
            cutoff_date = datetime.now(timezone.utc).replace(
                day=datetime.now(timezone.utc).day - days
            )
            result = self.collection.delete_many({
                'is_read': True,
                'created_at': {'$lt': cutoff_date}
            })
            return {'success': True, 'deleted': result.deleted_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}
