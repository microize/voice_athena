"""User API routes"""
import logging
import aiosqlite
from fastapi import APIRouter, HTTPException, Depends
from athena.core.config import settings
from athena.core.security import require_auth

router = APIRouter(prefix="/api", tags=["user"])
logger = logging.getLogger(__name__)

@router.get("/user/progress")
async def get_user_progress(user: dict = Depends(require_auth)):
    """Get user's coding progress statistics"""
    try:
        async with aiosqlite.connect(settings.DB_PATH) as db:
            cursor = await db.execute("""
                SELECT problems_solved, easy_solved, medium_solved, hard_solved, total_submissions, last_solved_at
                FROM user_progress WHERE user_id = ?
            """, (user["username"],))
            result = await cursor.fetchone()
            
            if result:
                return {
                    "problems_solved": result[0],
                    "easy_solved": result[1],
                    "medium_solved": result[2],
                    "hard_solved": result[3],
                    "total_submissions": result[4],
                    "last_solved_at": result[5]
                }
            else:
                return {
                    "problems_solved": 0,
                    "easy_solved": 0,
                    "medium_solved": 0,
                    "hard_solved": 0,
                    "total_submissions": 0,
                    "last_solved_at": None
                }
    except Exception as e:
        logger.error(f"Error fetching user progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch progress")