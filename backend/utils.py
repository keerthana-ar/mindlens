"""
Utility functions for MindLens
Helper functions for formatting, colors, and common operations
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import re

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    try:
        # Parse the timestamp
        if isinstance(timestamp_str, str):
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            dt = timestamp_str
        
        now = datetime.now()
        diff = now - dt.replace(tzinfo=None)
        
        # Format based on time difference
        if diff.days == 0:
            if diff.seconds < 3600:  # Less than 1 hour
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:  # Less than 24 hours
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            return dt.strftime("%B %d, %Y")
            
    except Exception as e:
        print(f"Error formatting timestamp: {e}")
        return "Unknown time"

def get_emotion_color(emotion: str) -> str:
    """Get color associated with emotion"""
    emotion_colors = {
        'joy': '#FFD700',      # Gold
        'love': '#FF69B4',     # Hot Pink
        'surprise': '#FF8C00', # Dark Orange
        'neutral': '#808080',  # Gray
        'fear': '#9370DB',     # Medium Purple
        'sadness': '#4169E1',  # Royal Blue
        'anger': '#DC143C'     # Crimson
    }
    return emotion_colors.get(emotion.lower(), '#667eea')

def get_emotion_emoji(emotion: str) -> str:
    """Get emoji associated with emotion"""
    emotion_emojis = {
        'joy': '😊',
        'love': '❤️',
        'surprise': '😲',
        'neutral': '😐',
        'fear': '😰',
        'sadness': '😢',
        'anger': '😠'
    }
    return emotion_emojis.get(emotion.lower(), '🤔')

def get_emotion_description(emotion: str) -> str:
    """Get description for emotion"""
    descriptions = {
        'joy': 'Feeling happy, content, and positive',
        'love': 'Experiencing affection, warmth, and connection',
        'surprise': 'Feeling amazed, shocked, or unexpected',
        'neutral': 'Balanced emotional state, neither positive nor negative',
        'fear': 'Experiencing anxiety, worry, or apprehension',
        'sadness': 'Feeling down, melancholy, or disappointed',
        'anger': 'Feeling frustrated, irritated, or upset'
    }
    return descriptions.get(emotion.lower(), 'An emotional state')

def clean_text(text: str) -> str:
    """Clean and normalize text input"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.,!?;:\'"()-]', '', text)
    
    return text

def calculate_reading_time(text: str) -> int:
    """Calculate estimated reading time in minutes"""
    if not text:
        return 0
    
    words = len(text.split())
    # Average reading speed is 200-250 words per minute
    reading_time = max(1, words // 200)
    return reading_time

def get_mood_score(emotion: str, confidence: float) -> float:
    """Convert emotion to mood score (1-10 scale)"""
    base_scores = {
        'joy': 9,
        'love': 8,
        'surprise': 6,
        'neutral': 5,
        'fear': 3,
        'sadness': 2,
        'anger': 2
    }
    
    base_score = base_scores.get(emotion.lower(), 5)
    # Adjust by confidence level
    adjusted_score = base_score * (confidence / 100)
    return round(adjusted_score, 1)

def generate_writing_prompt() -> str:
    """Generate a random writing prompt for inspiration"""
    prompts = [
        "What made you smile today?",
        "Describe a moment when you felt truly peaceful.",
        "What are you grateful for right now?",
        "Write about a challenge you overcame recently.",
        "What would you tell your younger self?",
        "Describe your ideal day from start to finish.",
        "What's something new you learned this week?",
        "Write about a person who has positively influenced your life.",
        "What are your hopes for tomorrow?",
        "Describe a place where you feel completely at ease.",
        "What's a small victory you achieved recently?",
        "Write about something that inspired you lately.",
        "What would you do if you had no fear?",
        "Describe a moment of unexpected kindness.",
        "What are you looking forward to most?"
    ]
    
    import random
    return random.choice(prompts)

def validate_journal_entry(content: str) -> Dict[str, Any]:
    """Validate journal entry content"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'word_count': 0,
        'char_count': 0
    }
    
    if not content or not content.strip():
        result['valid'] = False
        result['errors'].append("Journal entry cannot be empty")
        return result
    
    content = content.strip()
    result['char_count'] = len(content)
    result['word_count'] = len(content.split())
    
    if len(content) < 10:
        result['valid'] = False
        result['errors'].append("Journal entry is too short (minimum 10 characters)")
    
    if len(content) > 5000:
        result['valid'] = False
        result['errors'].append("Journal entry is too long (maximum 5000 characters)")
    
    if result['word_count'] < 3:
        result['warnings'].append("Very short entry - consider writing more for better emotion analysis")
    
    return result

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours} hour{'s' if hours != 1 else ''}"

def get_encouragement_message(emotion: str) -> str:
    """Get encouraging message based on emotion"""
    messages = {
        'joy': "It's wonderful to see you feeling so positive! 🌟",
        'love': "Love and connection are beautiful emotions to experience. 💕",
        'surprise': "Life's surprises can lead to amazing discoveries! ✨",
        'neutral': "Sometimes a balanced state is exactly what we need. 🧘",
        'fear': "It's okay to feel afraid - acknowledging fear is the first step to courage. 💪",
        'sadness': "Your feelings are valid. Remember that this too shall pass. 🌈",
        'anger': "It's natural to feel angry sometimes. Let's work through this together. 🤝"
    }
    return messages.get(emotion.lower(), "Thank you for sharing your thoughts with me. 🙏")