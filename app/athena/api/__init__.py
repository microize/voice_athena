"""API module for Athena"""
from fastapi import APIRouter
from athena.api.routes import auth, problems, database, interview, websockets, pages, user

def create_api_router() -> APIRouter:
    """Create and configure the main API router with all routes"""
    
    # Create main API router
    api_router = APIRouter()
    
    # Include all route modules
    api_router.include_router(auth.router)
    api_router.include_router(problems.router) 
    api_router.include_router(database.router)
    api_router.include_router(interview.router)
    api_router.include_router(websockets.router)
    api_router.include_router(pages.router)
    api_router.include_router(user.router)
    
    return api_router