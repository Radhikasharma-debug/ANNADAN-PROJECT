"""
AI & Machine Learning module for Annadan-A-Umeed
Includes: Smart Matching, Demand Prediction, Chatbot, Route Optimization
"""

from app.ai.matching import DonorNGOMatcher
from app.ai.demand_prediction import DemandPredictor
from app.ai.chatbot import ChatbotManager
from app.ai.route_optimization import RouteOptimizer

__all__ = [
    'DonorNGOMatcher',
    'DemandPredictor', 
    'ChatbotManager',
    'RouteOptimizer'
]
