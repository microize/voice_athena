"""API routes for Athena"""

# Import all route modules for easy access
from . import auth, problems, database, interview, websockets, pages

__all__ = ["auth", "problems", "database", "interview", "websockets", "pages"]