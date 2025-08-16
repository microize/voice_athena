"""User-related database operations"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import aiosqlite

from athena.core.config import settings
from athena.models.schemas import UserProgress

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user-related database operations"""
    
    @staticmethod
    async def get_user_progress(username: str) -> UserProgress:
        """Get user's coding progress and statistics"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                # Get submission statistics
                cursor = await db.execute("""
                    SELECT 
                        COUNT(*) as total_submissions,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as problems_solved,
                        MAX(created_at) as last_solved_at
                    FROM submissions 
                    WHERE user_id = ?
                """, (username,))
                
                stats = await cursor.fetchone()
                
                # Get difficulty breakdown (mock data for now)
                # In production, you'd calculate this from actual submissions
                total_solved = stats[1] if stats[1] else 0
                
                progress = UserProgress(
                    problems_solved=total_solved,
                    easy_solved=min(total_solved, 8),
                    medium_solved=min(max(0, total_solved - 8), 6),
                    hard_solved=max(0, total_solved - 14),
                    total_submissions=stats[0] if stats[0] else 0,
                    last_solved_at=datetime.fromisoformat(stats[2]) if stats[2] else None
                )
                
                return progress
                
        except Exception as e:
            logger.error(f"Error fetching user progress for {username}: {e}")
            # Return default progress on error
            return UserProgress()
    
    @staticmethod
    async def create_user_session(username: str, session_data: Dict[str, Any]) -> bool:
        """Create or update user session data"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_sessions (username, session_data, created_at)
                    VALUES (?, ?, ?)
                """, (username, str(session_data), datetime.utcnow().isoformat()))
                await db.commit()
                
                logger.info(f"Created/updated session for user {username}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating user session for {username}: {e}")
            return False
    
    @staticmethod
    async def get_user_session(username: str) -> Optional[Dict[str, Any]]:
        """Get user session data"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT session_data FROM user_sessions WHERE username = ?
                """, (username,))
                result = await cursor.fetchone()
                
                if result:
                    # In production, you'd properly parse the session data
                    return {"session_data": result[0]}
                
                return None
                
        except Exception as e:
            logger.error(f"Error fetching user session for {username}: {e}")
            return None
    
    @staticmethod
    async def record_submission(
        username: str,
        problem_id: int,
        code: str,
        language: str,
        status: str,
        runtime: Optional[int] = None,
        memory: Optional[int] = None
    ) -> int:
        """Record a code submission"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute("""
                    INSERT INTO submissions (
                        user_id, problem_id, code, language, status, runtime, memory, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    username,
                    problem_id,
                    code,
                    language,
                    status,
                    runtime,
                    memory,
                    datetime.utcnow().isoformat()
                ))
                submission_id = cursor.lastrowid
                await db.commit()
                
                logger.info(f"Recorded submission {submission_id} for user {username} on problem {problem_id}")
                return submission_id
                
        except Exception as e:
            logger.error(f"Error recording submission for {username}: {e}")
            raise
    
    @staticmethod
    async def get_user_submissions(username: str, problem_id: Optional[int] = None) -> list:
        """Get user's submission history"""
        try:
            query = """
                SELECT id, problem_id, code, language, status, runtime, memory, created_at
                FROM submissions WHERE user_id = ?
            """
            params = [username]
            
            if problem_id:
                query += " AND problem_id = ?"
                params.append(problem_id)
            
            query += " ORDER BY created_at DESC"
            
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute(query, params)
                results = await cursor.fetchall()
                
                submissions = []
                for row in results:
                    submissions.append({
                        "id": row[0],
                        "problem_id": row[1],
                        "code": row[2],
                        "language": row[3],
                        "status": row[4],
                        "runtime": row[5],
                        "memory": row[6],
                        "created_at": row[7]
                    })
                
                return submissions
                
        except Exception as e:
            logger.error(f"Error fetching submissions for {username}: {e}")
            return []