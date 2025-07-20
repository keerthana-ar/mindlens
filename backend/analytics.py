"""
Analytics and insights for MindLens
Provides emotion trends, patterns, and statistics
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import statistics

class EmotionAnalytics:
    def __init__(self, db_manager):
        """Initialize analytics with database manager"""
        self.db = db_manager
    
    def get_emotion_distribution(self, user_id: str, days: int = 30) -> Dict[str, int]:
        """Get emotion distribution over specified days"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT emotion, COUNT(*) as count
                    FROM journal_entries 
                    WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                    GROUP BY emotion
                    ORDER BY count DESC
                """.format(days), (user_id,))
                
                return dict(cursor.fetchall())
                
        except Exception as e:
            print(f"Error getting emotion distribution: {e}")
            return {}
    
    def get_mood_trends(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get mood trends over time with mood scoring"""
        try:
            # Emotion to mood score mapping (1-10 scale)
            emotion_scores = {
                'joy': 9, 'love': 8, 'surprise': 6, 'neutral': 5,
                'fear': 3, 'sadness': 2, 'anger': 2
            }
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DATE(timestamp) as date, emotion, emotion_score
                    FROM journal_entries 
                    WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                    ORDER BY date
                """.format(days), (user_id,))
                
                daily_moods = defaultdict(list)
                for row in cursor.fetchall():
                    date, emotion, score = row
                    base_score = emotion_scores.get(emotion, 5)
                    # Adjust base score by confidence (emotion_score)
                    adjusted_score = base_score * (score / 100)
                    daily_moods[date].append(adjusted_score)
                
                # Calculate daily averages
                trends = []
                for date, scores in daily_moods.items():
                    avg_mood = statistics.mean(scores)
                    trends.append({
                        'date': date,
                        'mood_score': round(avg_mood, 2),
                        'entry_count': len(scores)
                    })
                
                return sorted(trends, key=lambda x: x['date'])
                
        except Exception as e:
            print(f"Error getting mood trends: {e}")
            return []
    
    def get_weekly_summary(self, user_id: str) -> Dict:
        """Get weekly summary statistics"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Entries per week over last 8 weeks
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%W', timestamp) as week,
                        COUNT(*) as entries
                    FROM journal_entries 
                    WHERE user_id = ? AND timestamp >= date('now', '-56 days')
                    GROUP BY week
                    ORDER BY week
                """, (user_id,))
                
                weekly_data = cursor.fetchall()
                if not weekly_data:
                    return {'avg_entries_per_week': 0, 'trend': 'stable'}
                
                entry_counts = [row[1] for row in weekly_data]
                avg_entries = statistics.mean(entry_counts)
                
                # Determine trend
                if len(entry_counts) >= 2:
                    recent_avg = statistics.mean(entry_counts[-2:])
                    older_avg = statistics.mean(entry_counts[:-2]) if len(entry_counts) > 2 else entry_counts[0]
                    
                    if recent_avg > older_avg * 1.2:
                        trend = 'increasing'
                    elif recent_avg < older_avg * 0.8:
                        trend = 'decreasing'
                    else:
                        trend = 'stable'
                else:
                    trend = 'stable'
                
                return {
                    'avg_entries_per_week': round(avg_entries, 1),
                    'trend': trend,
                    'weekly_data': weekly_data
                }
                
        except Exception as e:
            print(f"Error getting weekly summary: {e}")
            return {'avg_entries_per_week': 0, 'trend': 'stable'}
    
    def get_writing_streak(self, user_id: str) -> int:
        """Calculate current writing streak in days"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT DATE(timestamp) as date
                    FROM journal_entries 
                    WHERE user_id = ?
                    ORDER BY date DESC
                """, (user_id,))
                
                dates = [datetime.strptime(row[0], '%Y-%m-%d').date() for row in cursor.fetchall()]
                
                if not dates:
                    return 0
                
                # Check if today or yesterday has an entry
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                
                if dates[0] not in [today, yesterday]:
                    return 0
                
                # Count consecutive days
                streak = 1
                current_date = dates[0]
                
                for date in dates[1:]:
                    expected_date = current_date - timedelta(days=1)
                    if date == expected_date:
                        streak += 1
                        current_date = date
                    else:
                        break
                
                return streak
                
        except Exception as e:
            print(f"Error calculating writing streak: {e}")
            return 0
    
    def get_emotion_patterns(self, user_id: str) -> Dict:
        """Analyze emotion patterns by time of day and day of week"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        strftime('%H', timestamp) as hour,
                        strftime('%w', timestamp) as day_of_week,
                        emotion
                    FROM journal_entries 
                    WHERE user_id = ? AND timestamp >= date('now', '-90 days')
                """, (user_id,))
                
                hourly_emotions = defaultdict(list)
                daily_emotions = defaultdict(list)
                
                for row in cursor.fetchall():
                    hour, day_of_week, emotion = row
                    hourly_emotions[int(hour)].append(emotion)
                    daily_emotions[int(day_of_week)].append(emotion)
                
                # Find most common emotions by hour and day
                hourly_patterns = {}
                for hour, emotions in hourly_emotions.items():
                    most_common = Counter(emotions).most_common(1)
                    if most_common:
                        hourly_patterns[hour] = most_common[0][0]
                
                daily_patterns = {}
                day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                for day, emotions in daily_emotions.items():
                    most_common = Counter(emotions).most_common(1)
                    if most_common:
                        daily_patterns[day_names[day]] = most_common[0][0]
                
                return {
                    'hourly_patterns': hourly_patterns,
                    'daily_patterns': daily_patterns
                }
                
        except Exception as e:
            print(f"Error analyzing emotion patterns: {e}")
            return {'hourly_patterns': {}, 'daily_patterns': {}}
    
    def get_word_analysis(self, user_id: str) -> Dict:
        """Analyze writing patterns and word usage"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT content, word_count, emotion
                    FROM journal_entries 
                    WHERE user_id = ? AND timestamp >= date('now', '-30 days')
                """, (user_id,))
                
                entries = cursor.fetchall()
                if not entries:
                    return {}
                
                # Calculate statistics
                word_counts = [row[1] for row in entries if row[1]]
                avg_words = statistics.mean(word_counts) if word_counts else 0
                
                # Emotion-specific word counts
                emotion_words = defaultdict(list)
                for content, word_count, emotion in entries:
                    if word_count:
                        emotion_words[emotion].append(word_count)
                
                emotion_avg_words = {}
                for emotion, counts in emotion_words.items():
                    emotion_avg_words[emotion] = statistics.mean(counts)
                
                return {
                    'avg_words_per_entry': round(avg_words, 1),
                    'total_entries': len(entries),
                    'emotion_word_averages': emotion_avg_words
                }
                
        except Exception as e:
            print(f"Error analyzing words: {e}")
            return {}
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get comprehensive user statistics"""
        return self.db.get_user_stats(user_id)
    
    def get_insights(self, user_id: str) -> List[str]:
        """Generate personalized insights based on user data"""
        insights = []
        
        try:
            # Get various analytics
            emotion_dist = self.get_emotion_distribution(user_id)
            streak = self.get_writing_streak(user_id)
            weekly_summary = self.get_weekly_summary(user_id)
            patterns = self.get_emotion_patterns(user_id)
            
            # Generate insights
            if emotion_dist:
                most_common = max(emotion_dist.items(), key=lambda x: x[1])
                insights.append(f"Your most frequent emotion this month is {most_common[0]} ({most_common[1]} entries)")
            
            if streak > 0:
                if streak == 1:
                    insights.append("Great job writing today! Keep the momentum going.")
                elif streak < 7:
                    insights.append(f"You're on a {streak}-day writing streak! Consistency is key to emotional awareness.")
                else:
                    insights.append(f"Amazing! You've maintained a {streak}-day writing streak. This shows real commitment to your mental wellness.")
            
            if weekly_summary.get('trend') == 'increasing':
                insights.append("You've been writing more frequently lately - this increased self-reflection is wonderful for personal growth!")
            
            if patterns.get('daily_patterns'):
                # Find most emotional day
                daily_emotions = patterns['daily_patterns']
                if daily_emotions:
                    insights.append("Consider how different days of the week affect your emotional state.")
            
            if not insights:
                insights.append("Keep writing to unlock personalized insights about your emotional patterns!")
            
            return insights[:3]  # Return top 3 insights
            
        except Exception as e:
            print(f"Error generating insights: {e}")
            return ["Continue journaling to discover insights about your emotional journey!"]