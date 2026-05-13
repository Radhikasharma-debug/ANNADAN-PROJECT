"""
AI Chatbot Manager
Handle conversations with users using pattern matching and optional AI integration
"""

import random
from datetime import datetime
from app.utils.time import utc_now

class ChatbotManager:
    """Manage chatbot conversations and responses"""
    
    # FAQ Knowledge Base
    FAQ_DATABASE = {
        'how_to_donate': {
            'triggers': ['how do i donate', 'post food', 'donate food', 'how to donate'],
            'response': '''To donate food:
1. Click "Post Food" on the dashboard
2. Enter food details (type, quantity, expiry)
3. Add location and photos
4. Submit
NGOs will see your donation and can request pickup.'''
        },
        'registration': {
            'triggers': ['how to register', 'sign up', 'create account', 'register'],
            'response': '''To register:
1. Click "Register" on the home page
2. Choose "Donor" or "NGO"
3. Fill in your details
4. Verify your email
5. Complete your profile
Your account is ready to use!'''
        },
        'ngo_verification': {
            'triggers': ['ngo verification', 'get verified', 'verify ngo', 'become verified'],
            'response': '''To get NGO verified:
1. Complete your NGO profile
2. Upload required documents
3. Provide registration certificate
4. Our team reviews (2-3 days)
5. Once approved, you get verified badge
This helps build trust with donors.'''
        },
        'food_safety': {
            'triggers': ['food safety', 'hygiene', 'health', 'fresh food'],
            'response': '''Food Safety Guidelines:
✓ Only donate fresh, unopened packages
✓ Check expiry dates
✓ Store at proper temperature
✓ Use insulated containers for delivery
✓ Handle with clean, sanitized hands
✓ Avoid cross-contamination
Your safety is our priority!'''
        },
        'delivery': {
            'triggers': ['delivery', 'pickup', 'how is food delivered', 'transportation'],
            'response': '''Food Delivery Process:
1. Donor posts food
2. Nearby NGO accepts request
3. NGO arranges pickup/delivery
4. Food is collected safely
5. NGO distributes to beneficiaries
6. Confirmation sent to donor
We partner with local delivery riders too!'''
        },
        'tracking': {
            'triggers': ['track donation', 'track food', 'where is my donation', 'status'],
            'response': '''Track Your Donation:
1. Go to "My Donations" in dashboard
2. Click on donation to see details
3. View NGO acceptance status
4. See pickup confirmation with photos
5. Get distribution completion updates
All updates sent to your phone & email!'''
        },
        'impact': {
            'triggers': ['impact', 'how many people', 'statistics', 'helped', 'beneficiaries'],
            'response': '''Your Impact:
Each donation helps real people! See:
- Total food donated (tons)
- Beneficiaries served
- Waste reduced
- Partner NGOs engaged
- Carbon footprint saved
Thank you for making a difference!'''
        },
        'payment': {
            'triggers': ['payment', 'cost', 'fee', 'charge', 'free'],
            'response': '''Donation is 100% FREE!
- No signup fees
- No posting fees
- No pickup charges
- No hidden costs
We operate on donations to keep this
platform accessible to all. Thank you!'''
        },
        'issues': {
            'triggers': ['problem', 'issue', 'complaint', 'error', 'not working'],
            'response': '''We\'re sorry you\'re experiencing issues.
Please contact our support team:
📧 Email: support@annadan.com
📱 Phone: +91-XXXX-XXXX-XXXX
⏰ Hours: 9 AM - 9 PM IST
We\'ll resolve it within 24 hours!'''
        },
        'privacy': {
            'triggers': ['privacy', 'data', 'security', 'personal info'],
            'response': '''Your Privacy is Protected:
✓ Data encrypted end-to-end
✓ No sharing with third parties
✓ GDPR & local law compliant
✓ Secure authentication
✓ Regular security audits
Read our full Privacy Policy on the website.'''
        }
    }
    
    # Contextual Responses
    CONTEXTUAL_RESPONSES = {
        'greeting': [
            'Hello! Welcome to Annadan-A-Umeed. How can I help you today?',
            'Hi there! 👋 What would you like to know about food donation?',
            'Namaste! 🙏 I\'m here to help you share food and save lives.'
        ],
        'gratitude': [
            'You\'re welcome! Is there anything else I can help with?',
            'Happy to help! Any other questions? 😊',
            'My pleasure! Feel free to ask anything else.'
        ],
        'unclear': [
            'I didn\'t quite understand. Could you rephrase that?',
            'I\'m not sure what you\'re asking. Can you provide more details?',
            'Hmm, could you ask differently? I\'m here to help!'
        ],
        'farewell': [
            'Thank you for using Annadan-A-Umeed! See you soon! 👋',
            'Great talking to you! Keep spreading food and love! 💚',
            'Goodbye! Remember, every donation saves a life. 🙏'
        ]
    }
    
    def __init__(self, db=None):
        self.db = db
        self.conversations = {}
        self.conversation_id_counter = 0
    
    def start_conversation(self, user_id):
        """Start a new conversation session"""
        self.conversation_id_counter += 1
        conv_id = f'conv_{user_id}_{self.conversation_id_counter}'
        
        self.conversations[conv_id] = {
            'user_id': user_id,
            'start_time': utc_now(),
            'messages': [],
            'context': {}
        }
        
        # Send greeting
        greeting = random.choice(self.CONTEXTUAL_RESPONSES['greeting'])
        
        return {
            'conversation_id': conv_id,
            'message': greeting,
            'timestamp': utc_now().isoformat()
        }
    
    def get_response(self, user_message, conversation_id=None, user_id=None):
        """Get AI chatbot response to user message"""
        try:
            # Normalize input
            user_message_lower = user_message.lower().strip()
            
            # Check for intent
            if self._is_greeting(user_message_lower):
                return {
                    'success': True,
                    'response': random.choice(self.CONTEXTUAL_RESPONSES['greeting']),
                    'type': 'greeting'
                }
            
            if self._is_gratitude(user_message_lower):
                return {
                    'success': True,
                    'response': random.choice(self.CONTEXTUAL_RESPONSES['gratitude']),
                    'type': 'gratitude'
                }
            
            if self._is_farewell(user_message_lower):
                return {
                    'success': True,
                    'response': random.choice(self.CONTEXTUAL_RESPONSES['farewell']),
                    'type': 'farewell'
                }
            
            # Match against FAQ
            matched_faq = self._match_faq(user_message_lower)
            
            if matched_faq:
                response = {
                    'success': True,
                    'response': matched_faq['response'],
                    'type': 'faq',
                    'category': matched_faq['category']
                }
            else:
                # Default fallback
                response = {
                    'success': True,
                    'response': self._get_fallback_response(),
                    'type': 'fallback',
                    'suggestion': 'contact_support'
                }
            
            # Store message if conversation exists
            if conversation_id and conversation_id in self.conversations:
                self.conversations[conversation_id]['messages'].append({
                    'user': user_message,
                    'bot': response['response'],
                    'timestamp': utc_now().isoformat()
                })
            
            return response
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error. Please try again.'
            }
    
    def _match_faq(self, user_message):
        """Match user message to FAQ category"""
        for category, faq_item in self.FAQ_DATABASE.items():
            triggers = faq_item.get('triggers', [])
            
            # Check if any trigger matches
            for trigger in triggers:
                if trigger in user_message:
                    return {
                        'category': category,
                        'response': faq_item['response']
                    }
        
        return None
    
    def _is_greeting(self, message):
        """Check if message is a greeting"""
        greetings = ['hi', 'hello', 'hey', 'namaste', 'howdy', 'greetings']
        return any(greeting in message for greeting in greetings)
    
    def _is_gratitude(self, message):
        """Check if message expresses gratitude"""
        gratitude_words = ['thanks', 'thank you', 'appreciate', 'grateful', 'cheers']
        return any(word in message for word in gratitude_words)
    
    def _is_farewell(self, message):
        """Check if message is farewell"""
        farewell_words = ['bye', 'goodbye', 'see you', 'take care', 'farewell']
        return any(word in message for word in farewell_words)
    
    def _get_fallback_response(self):
        """Get fallback response for unmatched queries"""
        fallback_responses = [
            'That\'s a great question! For detailed help, please check our FAQ or contact support.',
            'I\'m not sure about that. Would you like me to connect you with our support team?',
            'I don\'t have information on that topic, but our team can help! Contact support@annadan.com'
        ]
        return random.choice(fallback_responses)
    
    def get_conversation_history(self, conversation_id):
        """Get full conversation history"""
        if conversation_id not in self.conversations:
            return {'success': False, 'error': 'Conversation not found'}
        
        conv = self.conversations[conversation_id]
        
        return {
            'success': True,
            'conversation_id': conversation_id,
            'user_id': conv['user_id'],
            'start_time': conv['start_time'].isoformat(),
            'message_count': len(conv['messages']),
            'messages': conv['messages']
        }
    
    def get_faq_categories(self):
        """Get all FAQ categories"""
        return {
            'success': True,
            'categories': {
                category: {
                    'title': self._format_title(category),
                    'preview': self.FAQ_DATABASE[category]['response'][:100] + '...'
                }
                for category in self.FAQ_DATABASE.keys()
            }
        }
    
    def get_faq_by_category(self, category):
        """Get FAQ item by category"""
        if category not in self.FAQ_DATABASE:
            return {'success': False, 'error': 'Category not found'}
        
        faq = self.FAQ_DATABASE[category]
        
        return {
            'success': True,
            'category': category,
            'title': self._format_title(category),
            'content': faq['response'],
            'triggers': faq.get('triggers', [])
        }
    
    def _format_title(self, category):
        """Format category name as title"""
        return ' '.join(word.capitalize() for word in category.split('_'))
    
    def get_chatbot_stats(self):
        """Get chatbot usage statistics"""
        return {
            'success': True,
            'total_conversations': len(self.conversations),
            'faq_categories': len(self.FAQ_DATABASE),
            'faq_items': sum(len(item.get('triggers', [])) for item in self.FAQ_DATABASE.values())
        }
