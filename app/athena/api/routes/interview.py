"""Interview session API routes"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from athena.models.schemas import InterviewSession, UserProgress
from athena.core.security import require_auth
from athena.services.interview_service import InterviewService
from athena.services.user_service import UserService
from athena.core.dependencies import get_interview_service, get_user_service

router = APIRouter(prefix="/api", tags=["interview"])
logger = logging.getLogger(__name__)

@router.post("/start-interview")
async def start_interview(
    employee_id: Optional[str] = None, 
    user: dict = Depends(require_auth),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Start a new interview session"""
    try:
        session_id = await interview_service.create_interview_session(
            username=user["username"],
            employee_id=employee_id
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Interview session started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting interview session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start interview session")

@router.get("/user/progress")
async def get_user_progress(
    user: dict = Depends(require_auth),
    user_service: UserService = Depends(get_user_service)
):
    """Get user's coding progress"""
    try:
        progress = await user_service.get_user_progress(user["username"])
        return progress.dict()
        
    except Exception as e:
        logger.error(f"Error fetching user progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user progress")

@router.get("/sessions")
async def get_user_sessions(
    user: dict = Depends(require_auth),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Get user's interview sessions"""
    try:
        sessions = await interview_service.get_user_interview_sessions(user["username"])
        return {"sessions": [session.dict() for session in sessions]}
        
    except Exception as e:
        logger.error(f"Error fetching user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user sessions")

@router.get("/sessions/{session_id}")
async def get_session_details(
    session_id: str, 
    user: dict = Depends(require_auth),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Get details of a specific interview session"""
    try:
        session = await interview_service.get_interview_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get session activities
        activities = await interview_service.get_interview_activities(session_id)
        
        return {
            "session": session.dict(),
            "activities": activities
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch session details")