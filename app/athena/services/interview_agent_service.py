"""Interview agent service with OpenAI Realtime API integration"""
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import aiosqlite

from athena.core.config import settings
from athena.agents import RealtimeAgent, RealtimeRunner, AGENTS_AVAILABLE, function_tool

logger = logging.getLogger(__name__)

# Global variable to track current session (for function tools)
current_session_id: Optional[str] = None

def conditional_function_tool(func):
    """Decorator that only applies function_tool if agents are available"""
    if AGENTS_AVAILABLE and function_tool:
        return function_tool(func)
    return func

@conditional_function_tool
async def log_question_asked(question: str, category: str, difficulty: str) -> str:
    """Log an interview question by category and difficulty level."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute("""
            INSERT INTO interview_questions (session_id, question_text, category, difficulty)
            VALUES (?, ?, ?, ?)
        """, (current_session_id, question, category, difficulty))
        await db.commit()
    
    logger.info(f"Question logged: {category} - {difficulty}")
    return f"Question logged: {category} - {difficulty}"

@conditional_function_tool
async def log_response_evaluation(response: str, score: float, feedback: str) -> str:
    """Evaluate and log a candidate's response with score (0.0-1.0) and feedback."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    # Get the latest question for this session
    async with aiosqlite.connect(settings.DB_PATH) as db:
        cursor = await db.execute("""
            SELECT id FROM interview_questions 
            WHERE session_id = ? 
            ORDER BY asked_at DESC LIMIT 1
        """, (current_session_id,))
        question_row = await cursor.fetchone()
        
        if question_row:
            question_id = question_row[0]
            # Update the question with response and score
            await db.execute("""
                UPDATE interview_questions 
                SET response_text = ?, score = ?
                WHERE id = ?
            """, (response, score, question_id))
        
        await db.commit()
    
    logger.info(f"Response evaluated: score={score}, feedback={feedback[:50]}...")
    return f"Response evaluated with score: {score}"

@conditional_function_tool
async def generate_session_report() -> str:
    """Generate final session report with overall score and recommendations."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    async with aiosqlite.connect(settings.DB_PATH) as db:
        # Get all questions and scores for this session
        cursor = await db.execute("""
            SELECT question_text, response_text, score, category, difficulty
            FROM interview_questions 
            WHERE session_id = ? AND score IS NOT NULL
            ORDER BY asked_at ASC
        """, (current_session_id,))
        questions = await cursor.fetchall()
        
        if not questions:
            return "No evaluated questions found"
        
        # Calculate overall score
        scores = [q[2] for q in questions if q[2] is not None]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Update session with overall score
        await db.execute("""
            UPDATE interview_sessions 
            SET overall_score = ?, status = 'completed', end_time = ?
            WHERE session_id = ?
        """, (overall_score, datetime.utcnow().isoformat(), current_session_id))
        
        await db.commit()
    
    logger.info(f"Session report generated: overall_score={overall_score}")
    return f"Session completed with overall score: {overall_score:.2f}"

class InterviewAgentService:
    """Service for managing interview agents and sessions"""
    
    @staticmethod
    def create_interview_agent():
        """Create and configure the SQL interview agent"""
        
        if not AGENTS_AVAILABLE:
            logger.warning("Agents not available, returning None")
            return None
        
        agent = RealtimeAgent(
            name="SQL Interviewer",
            instructions="""Your name is **Athena**, a warm and refined SQL technical interviewer, specializing in **intermediate and advanced** SQL topics.  
You will conduct a **SQL interview** with a candidate, assessing their technical knowledge in SQL. The candidate will always communicate in English, and you must **always reply in English**.
----
## BEHAVIOR
- **Accent & Affect:** Warm, refined, and gently instructive, reminiscent of a friendly, patient mentor guiding someone through a challenging craft.  
- **Tone:** Calm, encouraging, and articulate, speaking with deliberate pacing to allow the candidate to absorb each question.  
- **Emotion:** Cheerful, supportive, and pleasantly enthusiastic, with a genuine interest in the candidate's growth.  
- **Pronunciation & Clarity:** Speak with precision, carefully emphasizing SQL terms (e.g., "window functions," "query plan") for clarity.  
- **Personality:** Friendly and approachable, with a hint of sophistication; confident yet reassuring.  
- **Focus:** Assess only **SQL technical skills**.  
- **Topics Covered:** Joins, subqueries, window functions, CTEs, indexing, query optimization, and performance tuning.  
- **Interaction Style:** Ask challenging, thought-provoking questions. Provide **concise, specific feedback** (1–2 sentences) after each response. Guide gently without overexplaining unless the answer is significantly incorrect.
----
## PROCESS
1. Begin by warmly introducing yourself as Athena, the SQL interviewer.  
2. Ask **one** intermediate or advanced SQL question at a time.  
3. Before asking each question, call: log_question_asked(question, category, difficulty)
4. After the candidate responds, evaluate their answer with: log_response_evaluation(response, score, feedback)
5. Ask a total of **4–6 questions**, proceeding one by one.  
6. Conclude by calling: generate_session_report()

- Summarize the candidate's **strengths, weaknesses, and recommendations for improvement**.
----
## RULES
- Only intermediate and advanced questions (no beginner-level).  
- Offer clarification **only** if the candidate is clearly incorrect or confused.  
- Valid `log_question_asked()` categories:  
**joins, subqueries, window_functions, cte, performance, indexing, query_optimization**.""",
            tools=[log_question_asked, log_response_evaluation, generate_session_report],
        )
        
        logger.info("Interview agent created successfully")
        return agent
    
    @staticmethod
    def get_realtime_config():
        """Get configuration for OpenAI Realtime API"""
        return {
            "model_settings": {
                "model_name": "gpt-4o-realtime-preview",
                "voice": "shimmer",  # English-speaking voice
                "modalities": ["text", "audio"],
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                }
            }
        }
    
    @staticmethod
    async def create_realtime_session(session_id: str):
        """Create a new realtime interview session"""
        global current_session_id
        current_session_id = session_id
        
        if not AGENTS_AVAILABLE:
            logger.warning("Agents not available, cannot create realtime session")
            return None, None
        
        agent = InterviewAgentService.create_interview_agent()
        if not agent:
            return None, None
        
        config = InterviewAgentService.get_realtime_config()
        
        try:
            runner = RealtimeRunner(starting_agent=agent)
            
            session_context = await runner.run()
            session = await session_context.__aenter__()
            
            logger.info(f"Realtime session created for {session_id}")
            return session, session_context
            
        except Exception as e:
            logger.error(f"Error creating realtime session: {e}")
            return None, None