"""Application settings and configuration."""

import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings configuration."""
    
    # Database
    DB_PATH: str = "interview_sessions.db"
    
    # Judge0 Configuration
    JUDGE0_API_URL: str = os.getenv("JUDGE0_API_URL", "https://judge0-ce.p.rapidapi.com")
    JUDGE0_API_KEY: str = os.getenv("JUDGE0_API_KEY", "")
    
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
    
    # Authentication
    DUMMY_USERS: Dict[str, Dict[str, str]] = {
        "admin": {"password": "admin", "name": "Administrator"},
        "test": {"password": "test123", "name": "Test User"},
        "user": {"password": "password", "name": "Regular User"}
    }
    
    # Session configuration
    SESSION_MAX_AGE: int = 24 * 60 * 60  # 24 hours
    
    # OpenAI/Realtime configuration
    REALTIME_MODEL_NAME: str = "gpt-4o-realtime-preview"
    REALTIME_VOICE: str = "shimmer"
    REALTIME_MODALITIES: list = ["text", "audio"]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Global settings instance
settings = Settings()