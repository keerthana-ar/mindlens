"""
Authentication and user management for MindLens
Simple session-based authentication for demo purposes
"""

import uuid
import streamlit as st
from typing import Optional

class AuthManager:
    def __init__(self):
        """Initialize authentication manager"""
        pass
    
    def get_or_create_user(self) -> str:
        """Get existing user ID or create new one"""
        if 'user_id' not in st.session_state:
            # Generate a unique user ID for this session
            user_id = str(uuid.uuid4())
            st.session_state.user_id = user_id
            
            # Initialize user in database
            from .database import DatabaseManager
            db = DatabaseManager()
            db.create_user(user_id)
            
            return user_id
        
        return st.session_state.user_id
    
    def get_current_user(self) -> Optional[str]:
        """Get current user ID if logged in"""
        return st.session_state.get('user_id')
    
    def logout(self):
        """Clear user session"""
        if 'user_id' in st.session_state:
            del st.session_state.user_id
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return 'user_id' in st.session_state
    
    def create_new_session(self) -> str:
        """Create a new user session (for demo purposes)"""
        if 'user_id' in st.session_state:
            del st.session_state.user_id
        
        return self.get_or_create_user()
    
    def get_user_display_name(self, user_id: str) -> str:
        """Get display name for user (simplified for demo)"""
        # In a real app, this would fetch from user profile
        return f"User {user_id[:8]}"