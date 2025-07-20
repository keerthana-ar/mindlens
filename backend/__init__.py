"""
Backend modules for MindLens
Enhanced with database, analytics, authentication, and utilities
"""

from .database import DatabaseManager
from .analytics import EmotionAnalytics
from .auth import AuthManager
from .utils import format_timestamp, get_emotion_color, get_emotion_emoji

__all__ = [
    'DatabaseManager',
    'EmotionAnalytics', 
    'AuthManager',
    'format_timestamp',
    'get_emotion_color',
    'get_emotion_emoji'
]