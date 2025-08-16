"""Interview session-related database operations"""
import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import aiosqlite

from athena.core.config import settings
from athena.models.schemas import InterviewSession

logger = logging.getLogger(__name__)

class InterviewService:
    """Service class for interview session-related database operations"""
    
    @staticmethod
    async def create_interview_session(
        username: str, 
        employee_id: Optional[str] = None
    ) -> str:
        """Create a new interview session"""
        try:
            session_id = str(uuid.uuid4())
            
            async with aiosqlite.connect(settings.DB_PATH) as db:
                await db.execute("""
                    INSERT INTO interview_sessions (
                        session_id, username, employee_id, start_time, status
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    username,
                    employee_id,
                    datetime.utcnow().isoformat(),
                    "active"
                ))
                await db.commit()
                
                logger.info(f"Created interview session {session_id} for user {username}")
                return session_id
                
        except Exception as e:
            logger.error(f"Error creating interview session: {e}")
            raise
    
    @staticmethod
    async def get_interview_session(session_id: str) -> Optional[InterviewSession]:
        """Get interview session by ID"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT session_id, username, employee_id, start_time, status, end_time
                    FROM interview_sessions WHERE session_id = ?
                """, (session_id,))
                result = await cursor.fetchone()
                
                if not result:
                    return None
                
                session = InterviewSession(
                    session_id=result[0],
                    employee_id=result[2],
                    start_time=datetime.fromisoformat(result[3]),
                    status=result[4]
                )
                
                return session
                
        except Exception as e:
            logger.error(f"Error fetching interview session {session_id}: {e}")
            return None
    
    @staticmethod
    async def update_interview_session_status(
        session_id: str, 
        status: str,
        end_time: Optional[datetime] = None
    ) -> bool:
        """Update interview session status"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                if end_time:
                    await db.execute("""
                        UPDATE interview_sessions 
                        SET status = ?, end_time = ? 
                        WHERE session_id = ?
                    """, (status, end_time.isoformat(), session_id))
                else:
                    await db.execute("""
                        UPDATE interview_sessions 
                        SET status = ? 
                        WHERE session_id = ?
                    """, (status, session_id))
                
                await db.commit()
                
                logger.info(f"Updated interview session {session_id} status to {status}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating interview session {session_id}: {e}")
            return False
    
    @staticmethod
    async def get_user_interview_sessions(username: str) -> List[InterviewSession]:
        """Get all interview sessions for a user"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT session_id, username, employee_id, start_time, status, end_time
                    FROM interview_sessions 
                    WHERE username = ?
                    ORDER BY start_time DESC
                """, (username,))
                results = await cursor.fetchall()
                
                sessions = []
                for row in results:
                    session = InterviewSession(
                        session_id=row[0],
                        employee_id=row[2],
                        start_time=datetime.fromisoformat(row[3]),
                        status=row[4]
                    )
                    sessions.append(session)
                
                return sessions
                
        except Exception as e:
            logger.error(f"Error fetching interview sessions for {username}: {e}")
            return []
    
    @staticmethod
    async def record_interview_activity(
        session_id: str,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> bool:
        """Record activity within an interview session"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                await db.execute("""
                    INSERT INTO interview_activities (
                        session_id, activity_type, activity_data, timestamp
                    ) VALUES (?, ?, ?, ?)
                """, (
                    session_id,
                    activity_type,
                    str(activity_data),  # In production, use proper JSON serialization
                    datetime.utcnow().isoformat()
                ))
                await db.commit()
                
                logger.debug(f"Recorded activity {activity_type} for session {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error recording interview activity: {e}")
            return False
    
    @staticmethod
    async def get_interview_activities(session_id: str) -> List[Dict[str, Any]]:
        """Get all activities for an interview session"""
        try:
            async with aiosqlite.connect(settings.DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT activity_type, activity_data, timestamp
                    FROM interview_activities 
                    WHERE session_id = ?
                    ORDER BY timestamp
                """, (session_id,))
                results = await cursor.fetchall()
                
                activities = []
                for row in results:
                    activities.append({
                        "activity_type": row[0],
                        "activity_data": row[1],  # In production, parse JSON
                        "timestamp": row[2]
                    })
                
                return activities
                
        except Exception as e:
            logger.error(f"Error fetching interview activities for {session_id}: {e}")
            return []