"""
Database management for MindLens
Handles journal entries, user data, and persistence
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "mindlens.db"):
        """Initialize database connection and create tables"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    settings TEXT DEFAULT '{}'
                )
            """)
            
            # Journal entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    emotion_score REAL NOT NULL,
                    reflection TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    word_count INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Emotion history table for analytics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emotion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    score REAL NOT NULL,
                    date DATE NOT NULL,
                    entry_count INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
    
    def create_user(self, user_id: str) -> bool:
        """Create a new user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO users (id) VALUES (?)",
                    (user_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def save_entry(self, user_id: str, content: str, emotion: str, 
                   emotion_score: float, reflection: str = None) -> Optional[int]:
        """Save a journal entry and return entry ID"""
        try:
            word_count = len(content.split())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert journal entry
                cursor.execute("""
                    INSERT INTO journal_entries 
                    (user_id, content, emotion, emotion_score, reflection, word_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, content, emotion, emotion_score, reflection, word_count))
                
                entry_id = cursor.lastrowid
                
                # Update emotion history for analytics
                today = datetime.now().date()
                cursor.execute("""
                    INSERT OR REPLACE INTO emotion_history 
                    (user_id, emotion, score, date, entry_count)
                    VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT entry_count FROM emotion_history 
                                WHERE user_id = ? AND emotion = ? AND date = ?), 0) + 1)
                """, (user_id, emotion, emotion_score, today, user_id, emotion, today))
                
                conn.commit()
                return entry_id
                
        except Exception as e:
            print(f"Error saving entry: {e}")
            return None
    
    def get_user_entries(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's journal entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, content, emotion, emotion_score, reflection, 
                           timestamp, word_count
                    FROM journal_entries 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                entries = []
                for row in cursor.fetchall():
                    entries.append({
                        'id': row[0],
                        'content': row[1],
                        'emotion': row[2],
                        'emotion_score': row[3],
                        'reflection': row[4],
                        'timestamp': row[5],
                        'word_count': row[6]
                    })
                
                return entries
                
        except Exception as e:
            print(f"Error getting entries: {e}")
            return []
    
    def get_entry_by_id(self, entry_id: int) -> Optional[Dict]:
        """Get a specific journal entry by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, content, emotion, emotion_score, 
                           reflection, timestamp, word_count
                    FROM journal_entries 
                    WHERE id = ?
                """, (entry_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'user_id': row[1],
                        'content': row[2],
                        'emotion': row[3],
                        'emotion_score': row[4],
                        'reflection': row[5],
                        'timestamp': row[6],
                        'word_count': row[7]
                    }
                return None
                
        except Exception as e:
            print(f"Error getting entry: {e}")
            return None
    
    def search_entries(self, user_id: str, query: str, emotion_filter: str = None) -> List[Dict]:
        """Search user's entries by content and optionally filter by emotion"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                sql = """
                    SELECT id, content, emotion, emotion_score, reflection, 
                           timestamp, word_count
                    FROM journal_entries 
                    WHERE user_id = ? AND content LIKE ?
                """
                params = [user_id, f"%{query}%"]
                
                if emotion_filter:
                    sql += " AND emotion = ?"
                    params.append(emotion_filter)
                
                sql += " ORDER BY timestamp DESC LIMIT 20"
                
                cursor.execute(sql, params)
                
                entries = []
                for row in cursor.fetchall():
                    entries.append({
                        'id': row[0],
                        'content': row[1],
                        'emotion': row[2],
                        'emotion_score': row[3],
                        'reflection': row[4],
                        'timestamp': row[5],
                        'word_count': row[6]
                    })
                
                return entries
                
        except Exception as e:
            print(f"Error searching entries: {e}")
            return []
    
    def delete_entry(self, entry_id: int, user_id: str) -> bool:
        """Delete a journal entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM journal_entries 
                    WHERE id = ? AND user_id = ?
                """, (entry_id, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get basic user statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total entries
                cursor.execute("""
                    SELECT COUNT(*) FROM journal_entries WHERE user_id = ?
                """, (user_id,))
                total_entries = cursor.fetchone()[0]
                
                # Entries this week
                cursor.execute("""
                    SELECT COUNT(*) FROM journal_entries 
                    WHERE user_id = ? AND timestamp >= date('now', '-7 days')
                """, (user_id,))
                entries_this_week = cursor.fetchone()[0]
                
                # Most common emotion
                cursor.execute("""
                    SELECT emotion, COUNT(*) as count 
                    FROM journal_entries 
                    WHERE user_id = ? 
                    GROUP BY emotion 
                    ORDER BY count DESC 
                    LIMIT 1
                """, (user_id,))
                
                most_common = cursor.fetchone()
                most_common_emotion = most_common[0] if most_common else "neutral"
                
                return {
                    'total_entries': total_entries,
                    'entries_this_week': entries_this_week,
                    'most_common_emotion': most_common_emotion
                }
                
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {'total_entries': 0, 'entries_this_week': 0, 'most_common_emotion': 'neutral'}
    
    def update_user_settings(self, user_id: str, settings: Dict) -> bool:
        """Update user settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET settings = ? WHERE id = ?
                """, (json.dumps(settings), user_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False
    
    def get_user_settings(self, user_id: str) -> Dict:
        """Get user settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT settings FROM users WHERE id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row and row[0]:
                    return json.loads(row[0])
                return {}
                
        except Exception as e:
            print(f"Error getting settings: {e}")
            return {}