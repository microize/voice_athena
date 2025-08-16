"""Custom exceptions for Athena application"""
from typing import Optional, Dict, Any

class AthenaException(Exception):
    """Base exception for Athena application"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

class DatabaseError(AthenaException):
    """Database-related errors"""
    pass

class AuthenticationError(AthenaException):
    """Authentication-related errors"""
    pass

class AuthorizationError(AthenaException):
    """Authorization-related errors"""
    pass

class ValidationError(AthenaException):
    """Data validation errors"""
    pass

class ExternalServiceError(AthenaException):
    """External service integration errors"""
    pass

class ProblemNotFoundError(AthenaException):
    """Problem not found error"""
    
    def __init__(self, problem_id: int):
        super().__init__(
            message=f"Problem with ID {problem_id} not found",
            error_code="PROBLEM_NOT_FOUND",
            details={"problem_id": problem_id}
        )

class SessionNotFoundError(AthenaException):
    """Session not found error"""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session with ID {session_id} not found",
            error_code="SESSION_NOT_FOUND",
            details={"session_id": session_id}
        )

class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials error"""
    
    def __init__(self):
        super().__init__(
            message="Invalid username or password",
            error_code="INVALID_CREDENTIALS"
        )

class ConfigurationError(AthenaException):
    """Configuration-related errors"""
    pass