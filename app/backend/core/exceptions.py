"""Custom exceptions for the application."""


class CodePlatformException(Exception):
    """Base exception for the code platform."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(CodePlatformException):
    """Exception raised for authentication failures."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class ValidationError(CodePlatformException):
    """Exception raised for validation failures."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400)


class ProblemNotFoundError(CodePlatformException):
    """Exception raised when a problem is not found."""
    
    def __init__(self, problem_id: int):
        super().__init__(f"Problem with ID {problem_id} not found", status_code=404)


class CodeExecutionError(CodePlatformException):
    """Exception raised for code execution failures."""
    
    def __init__(self, message: str = "Code execution failed"):
        super().__init__(message, status_code=500)


class DatabaseError(CodePlatformException):
    """Exception raised for database operations."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)