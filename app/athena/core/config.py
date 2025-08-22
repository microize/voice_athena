"""Configuration settings for Athena"""
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings with validation and type hints"""
    
    # API Configuration
    JUDGE0_API_URL: str = os.getenv("JUDGE0_API_URL", "https://judge0-ce.p.rapidapi.com")
    JUDGE0_API_KEY: str = os.getenv("JUDGE0_API_KEY") or os.getenv("RAPIDAPI_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database Configuration
    DB_PATH: str = os.getenv("DB_PATH", "data/interview_sessions.db")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8004"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security Configuration
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", os.urandom(32).hex())
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "10"))
    LOGIN_ATTEMPT_WINDOW: int = int(os.getenv("LOGIN_ATTEMPT_WINDOW", "900"))  # 15 minutes
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Judge0 Language IDs
    SUPPORTED_LANGUAGES: Dict[str, int] = {
        "python": 71,      # Python 3.8.1
        "javascript": 63,  # Node.js 12.14.0
        "java": 62,        # Java OpenJDK 13.0.1
        "cpp": 54,         # C++ GCC 9.2.0
        "csharp": 51,      # C# Mono 6.6.0.161
        "go": 60,          # Go 1.13.5
        "rust": 73,        # Rust 1.40.0
        "php": 68,         # PHP 7.4.1
        "ruby": 72         # Ruby 2.7.0
    }
    
    # Default Users - ONLY for development. Use strong passwords!
    DEFAULT_USERS: Dict[str, str] = {
        "admin": os.getenv("ADMIN_PASSWORD", "Admin123!@#SecureP@ss"),
        "demo": os.getenv("DEMO_PASSWORD", "Demo456!@#SecureP@ss")
    }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate critical configuration"""
        if not cls.OPENAI_API_KEY:
            logging.warning("OPENAI_API_KEY not configured - some features will be disabled")
        
        if not cls.JUDGE0_API_KEY:
            logging.warning("JUDGE0_API_KEY not configured - code execution will be disabled")
        
        return True

# Global settings instance
settings = Settings()

# Backward compatibility exports
DB_PATH = settings.DB_PATH
SUPPORTED_LANGUAGES = settings.SUPPORTED_LANGUAGES
JUDGE0_API_URL = settings.JUDGE0_API_URL
JUDGE0_API_KEY = settings.JUDGE0_API_KEY
OPENAI_API_KEY = settings.OPENAI_API_KEY