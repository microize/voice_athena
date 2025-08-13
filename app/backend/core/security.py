"""Security utilities and authentication."""

import secrets
import hashlib
from typing import Dict, Optional

from ..config.settings import settings


class SecurityService:
    """Security service for authentication and session management."""
    
    def __init__(self):
        # Simple session store (in production, use Redis or database)
        self.active_sessions: Dict[str, Dict] = {}
    
    def generate_session_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password: str) -> str:
        """Simple password hashing for demo purposes."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials."""
        if username in settings.DUMMY_USERS and settings.DUMMY_USERS[username]["password"] == password:
            return True
        return False
    
    def create_session(self, username: str) -> str:
        """Create a new user session and return the session token."""
        session_token = self.generate_session_token()
        
        self.active_sessions[session_token] = {
            "username": username,
            "name": settings.DUMMY_USERS[username]["name"]
        }
        
        return session_token
    
    def get_user_from_session(self, session_token: Optional[str]) -> Optional[Dict]:
        """Get user information from session token."""
        if session_token and session_token in self.active_sessions:
            return self.active_sessions[session_token]
        return None
    
    def invalidate_session(self, session_token: Optional[str]) -> bool:
        """Invalidate a user session."""
        if session_token and session_token in self.active_sessions:
            del self.active_sessions[session_token]
            return True
        return False
    
    def validate_sql_query(self, query: str) -> bool:
        """Basic security validation for SQL queries."""
        query_upper = query.upper().strip()
        allowed_commands = ['SELECT', 'WITH', 'PRAGMA TABLE_INFO']
        
        return any(query_upper.startswith(cmd) for cmd in allowed_commands)