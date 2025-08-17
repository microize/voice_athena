"""Security and authentication utilities"""
import secrets
import hashlib
import uuid
import logging
import bcrypt
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Cookie, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from athena.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBasic()

# In-memory session storage (in production, use Redis or database)
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Rate limiting storage (in production, use Redis)
LOGIN_ATTEMPTS: Dict[str, Dict[str, Any]] = {}
RATE_LIMIT_STORAGE: Dict[str, Dict[str, Any]] = {}

class SecurityManager:
    """Centralized security management"""
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            # Fallback for plain text passwords (dev only) - deprecated
            logger.warning("Using insecure plain text password comparison")
            return password == hashed
    
    @staticmethod
    def check_rate_limit(identifier: str, max_requests: int = None, window: int = None) -> bool:
        """Check if request is within rate limits"""
        max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        window = window or settings.RATE_LIMIT_WINDOW
        
        current_time = time.time()
        
        if identifier not in RATE_LIMIT_STORAGE:
            RATE_LIMIT_STORAGE[identifier] = {"requests": [], "blocked_until": 0}
        
        user_data = RATE_LIMIT_STORAGE[identifier]
        
        # Check if user is currently blocked
        if current_time < user_data["blocked_until"]:
            return False
        
        # Clean old requests outside the window
        user_data["requests"] = [
            req_time for req_time in user_data["requests"]
            if current_time - req_time < window
        ]
        
        # Check if limit exceeded
        if len(user_data["requests"]) >= max_requests:
            user_data["blocked_until"] = current_time + window
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        user_data["requests"].append(current_time)
        return True
    
    @staticmethod
    def check_login_attempts(identifier: str) -> bool:
        """Check if login attempts are within limits"""
        current_time = time.time()
        
        if identifier not in LOGIN_ATTEMPTS:
            LOGIN_ATTEMPTS[identifier] = {"attempts": [], "blocked_until": 0}
        
        user_data = LOGIN_ATTEMPTS[identifier]
        
        # Check if user is currently blocked
        if current_time < user_data["blocked_until"]:
            return False
        
        # Clean old attempts outside the window
        user_data["attempts"] = [
            attempt_time for attempt_time in user_data["attempts"]
            if current_time - attempt_time < settings.LOGIN_ATTEMPT_WINDOW
        ]
        
        # Check if limit exceeded
        if len(user_data["attempts"]) >= settings.MAX_LOGIN_ATTEMPTS:
            user_data["blocked_until"] = current_time + settings.LOGIN_ATTEMPT_WINDOW
            logger.warning(f"Login attempts exceeded for {identifier}")
            return False
        
        return True
    
    @staticmethod
    def record_failed_login(identifier: str):
        """Record a failed login attempt"""
        current_time = time.time()
        
        if identifier not in LOGIN_ATTEMPTS:
            LOGIN_ATTEMPTS[identifier] = {"attempts": [], "blocked_until": 0}
        
        LOGIN_ATTEMPTS[identifier]["attempts"].append(current_time)
    
    @staticmethod
    def verify_user(username: str, password: str, client_ip: str = "unknown") -> bool:
        """Verify user credentials with rate limiting"""
        # Input validation
        if not username or not password:
            return False
        
        if len(username) > 50 or len(password) > 200:
            logger.warning(f"Suspicious login attempt with oversized credentials from {client_ip}")
            return False
        
        # Check rate limiting
        if not SecurityManager.check_login_attempts(client_ip):
            logger.warning(f"Login rate limit exceeded for IP: {client_ip}")
            return False
        
        if username not in settings.DEFAULT_USERS:
            SecurityManager.record_failed_login(client_ip)
            logger.warning(f"Failed login attempt for unknown user: {username} from {client_ip}")
            return False
        
        stored_password = settings.DEFAULT_USERS[username]
        
        # Verify password
        is_valid = SecurityManager.verify_password(password, stored_password)
        
        if not is_valid:
            SecurityManager.record_failed_login(client_ip)
            logger.warning(f"Failed login attempt for user: {username} from {client_ip}")
        
        return is_valid
    
    @staticmethod
    def create_session(username: str) -> str:
        """Create a new session"""
        session_token = SecurityManager.generate_session_token()
        ACTIVE_SESSIONS[session_token] = {
            "username": username,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        logger.info(f"Created session for user: {username}")
        return session_token
    
    @staticmethod
    def get_session(session_token: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if not session_token or session_token not in ACTIVE_SESSIONS:
            return None
        
        session = ACTIVE_SESSIONS[session_token]
        
        # Check if session is expired
        if datetime.utcnow() > session["expires_at"]:
            SecurityManager.invalidate_session(session_token)
            return None
        
        # Update last activity
        session["last_activity"] = datetime.utcnow()
        return session
    
    @staticmethod
    def invalidate_session(session_token: str) -> bool:
        """Invalidate a session"""
        if session_token in ACTIVE_SESSIONS:
            username = ACTIVE_SESSIONS[session_token].get("username", "unknown")
            del ACTIVE_SESSIONS[session_token]
            logger.info(f"Invalidated session for user: {username}")
            return True
        return False
    
    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions"""
        current_time = datetime.utcnow()
        expired_tokens = [
            token for token, session in ACTIVE_SESSIONS.items()
            if current_time > session["expires_at"]
        ]
        
        for token in expired_tokens:
            username = ACTIVE_SESSIONS[token].get("username", "unknown")
            del ACTIVE_SESSIONS[token]
            logger.info(f"Cleaned up expired session for user: {username}")
        
        return len(expired_tokens)

# Dependency functions
def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current authenticated user from various auth methods"""
    
    # Method 1: Session cookie
    cookie_token = request.cookies.get("session_token")
    
    if cookie_token:
        session = SecurityManager.get_session(cookie_token)
        if session:
            return {"username": session["username"], "session_token": cookie_token}
    
    # Method 2: Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            if auth_header.startswith("Bearer "):
                # JWT or session token
                token = auth_header.split(" ")[1]
                session = SecurityManager.get_session(token)
                if session:
                    return {"username": session["username"], "session_token": token}
            
            elif auth_header.startswith("Basic "):
                # Basic auth
                import base64
                encoded_credentials = auth_header.split(" ")[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
                username, password = decoded_credentials.split(":", 1)
                
                if SecurityManager.verify_user(username, password):
                    return {"username": username}
                    
        except Exception as e:
            logger.warning(f"Auth header parsing failed: {e}")
    
    return None

def require_auth(request: Request) -> Dict[str, Any]:
    """Dependency to require authentication"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def optional_auth(request: Request) -> Optional[Dict[str, Any]]:
    """Optional authentication dependency"""
    return get_current_user(request)

# Backward compatibility functions
def generate_session_token() -> str:
    return SecurityManager.generate_session_token()

def hash_password(password: str) -> str:
    return SecurityManager.hash_password(password)

def verify_user(username: str, password: str) -> bool:
    return SecurityManager.verify_user(username, password)