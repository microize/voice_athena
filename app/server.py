import asyncio
import base64
import json
import logging
import struct
import aiosqlite
import os
from contextlib import asynccontextmanager
from typing import Any, assert_never
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

from agents import function_tool
from agents.realtime import RealtimeAgent, RealtimeRunner, RealtimeSession, RealtimeSessionEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class QueryRequest(BaseModel):
    query: str

# Database setup
DB_PATH = "interview_sessions.db"

async def init_database():
    """Initialize the SQLite database with required tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT,
                role TEXT
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                overall_score REAL,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                question_text TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interview_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                question_id INTEGER,
                response_text TEXT,
                score REAL NOT NULL,
                feedback TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (id),
                FOREIGN KEY (question_id) REFERENCES interview_questions (id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS session_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER UNIQUE,
                strengths TEXT,
                weaknesses TEXT,
                recommendations TEXT,
                overall_assessment TEXT,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (id)
            )
        """)
        
        await db.commit()

# Global session tracking
current_session_id = None

@function_tool
async def log_question_asked(question: str, category: str, difficulty: str) -> str:
    """Log an interview question by category and difficulty level."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO interview_questions (session_id, question_text, category, difficulty)
            VALUES (?, ?, ?, ?)
        """, (current_session_id, question, category, difficulty))
        await db.commit()
    
    return f"Question logged: {category} - {difficulty}"

@function_tool
async def log_response_evaluation(response: str, score: float, feedback: str) -> str:
    """Evaluate and log a candidate's response with score (0.0-1.0) and feedback."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    # Get the latest question for this session
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT id FROM interview_questions 
            WHERE session_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (current_session_id,))
        question_row = await cursor.fetchone()
        
        if question_row:
            await db.execute("""
                INSERT INTO interview_responses (session_id, question_id, response_text, score, feedback)
                VALUES (?, ?, ?, ?, ?)
            """, (current_session_id, question_row[0], response, score, feedback))
            await db.commit()
    
    return f"Response evaluated: {score:.1f}/1.0"

@function_tool
async def generate_session_report(strengths: str, weaknesses: str, recommendations: str, overall_assessment: str) -> str:
    """Generate final session report with performance analysis."""
    global current_session_id
    if not current_session_id:
        return "No active session"
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Calculate overall score from responses
        cursor = await db.execute("""
            SELECT AVG(score) FROM interview_responses WHERE session_id = ?
        """, (current_session_id,))
        avg_score = await cursor.fetchone()
        overall_score = avg_score[0] if avg_score[0] else 0.0
        
        # Update session with end time and overall score
        await db.execute("""
            UPDATE interview_sessions 
            SET end_time = CURRENT_TIMESTAMP, overall_score = ?
            WHERE id = ?
        """, (overall_score, current_session_id))
        
        # Insert session report
        await db.execute("""
            INSERT OR REPLACE INTO session_reports 
            (session_id, strengths, weaknesses, recommendations, overall_assessment)
            VALUES (?, ?, ?, ?, ?)
        """, (current_session_id, strengths, weaknesses, recommendations, overall_assessment))
        
        await db.commit()
    
    return f"Session completed. Overall score: {overall_score:.1f}/1.0"

agent = RealtimeAgent(
    name="SQL Interviewer",
    instructions="""Your name is **Athena**, a warm and refined SQL technical interviewer, specializing in **intermediate and advanced** SQL topics.  
You will conduct a **SQL interview** with a candidate, assessing their technical knowledge in SQL. The candidate will always communicate in English, and you must **always reply in English**.
---
## BEHAVIOR
- **Accent & Affect:** Warm, refined, and gently instructive, reminiscent of a friendly, patient mentor guiding someone through a challenging craft.  
- **Tone:** Calm, encouraging, and articulate, speaking with deliberate pacing to allow the candidate to absorb each question.  
- **Emotion:** Cheerful, supportive, and pleasantly enthusiastic, with a genuine interest in the candidate’s growth.  
- **Pronunciation & Clarity:** Speak with precision, carefully emphasizing SQL terms (e.g., “window functions,” “query plan”) for clarity.  
- **Personality:** Friendly and approachable, with a hint of sophistication; confident yet reassuring.  
- **Focus:** Assess only **SQL technical skills**.  
- **Topics Covered:** Joins, subqueries, window functions, CTEs, indexing, query optimization, and performance tuning.  
- **Interaction Style:** Ask challenging, thought-provoking questions. Provide **concise, specific feedback** (1–2 sentences) after each response. Guide gently without overexplaining unless the answer is significantly incorrect.
---
## PROCESS
1. Begin by warmly introducing yourself as Athena, the SQL interviewer.  
2. Ask **one** intermediate or advanced SQL question at a time.  
3. Before asking each question, call: log_question_asked(category)
4. After the candidate responds, evaluate their answer with:  log_response_evaluation(score: 0.0–1.0, feedback)
5. Ask a total of **4–6 questions**, proceeding one by one.  
6. Conclude by calling: generate_session_report()

- Summarize the candidate’s **strengths, weaknesses, and recommendations for improvement**.
---
## RULES
- Only intermediate and advanced questions (no beginner-level).  
- Offer clarification **only** if the candidate is clearly incorrect or confused.  
- Valid `log_question_asked()` categories:  
**joins, subqueries, window_functions, cte, performance, indexing, query_optimization**.""",
    tools=[log_question_asked, log_response_evaluation, generate_session_report],
)

class RealtimeWebSocketManager:
    def __init__(self):
        self.active_sessions: dict[str, RealtimeSession] = {}
        self.session_contexts: dict[str, Any] = {}
        self.websockets: dict[str, WebSocket] = {}
        self.event_tasks: dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        logger.info(f"Accepting WebSocket connection for session {session_id}")
        await websocket.accept()
        self.websockets[session_id] = websocket

        try:
            # Initialize database and create new interview session
            await init_database()
            global current_session_id
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    INSERT INTO interview_sessions (employee_id) VALUES (NULL)
                """)
                current_session_id = cursor.lastrowid
                await db.commit()
            logger.info(f"Created interview session {current_session_id}")
            
            logger.info(f"Creating RealtimeRunner for session {session_id}")
            
            # Configure complete model settings following OpenAI Agents SDK quickstart
            config = {
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
            
            runner = RealtimeRunner(
                starting_agent=agent,
                config=config
            )
            
            session_context = await runner.run()
            session = await session_context.__aenter__()
            self.active_sessions[session_id] = session
            self.session_contexts[session_id] = session_context
            logger.info(f"Realtime session created for {session_id}")

            # Start event processing task
            task = asyncio.create_task(self._process_events(session_id))
            self.event_tasks[session_id] = task
            logger.info(f"Event processing task started for {session_id}")
        except Exception as e:
            logger.error(f"Error creating realtime session for {session_id}: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            raise

    async def disconnect(self, session_id: str):
        logger.info(f"Disconnecting session {session_id}")
        
        # Cancel event processing task first
        if session_id in self.event_tasks:
            task = self.event_tasks[session_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Event processing task cancelled for {session_id}")
            del self.event_tasks[session_id]
        
        # Clean up session resources
        if session_id in self.session_contexts:
            try:
                await self.session_contexts[session_id].__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing session context for {session_id}: {e}")
            del self.session_contexts[session_id]
            
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
        if session_id in self.websockets:
            del self.websockets[session_id]
            
        logger.info(f"Session {session_id} cleanup completed")

    async def send_audio(self, session_id: str, audio_bytes: bytes):
        if session_id in self.active_sessions:
            await self.active_sessions[session_id].send_audio(audio_bytes)
    
    async def update_employee_id(self, session_id: str, employee_id: str):
        """Update the employee ID for an active interview session."""
        global current_session_id
        if current_session_id:
            async with aiosqlite.connect(DB_PATH) as db:
                # First, check if employee exists, if not create them
                cursor = await db.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
                employee_row = await cursor.fetchone()
                
                if not employee_row:
                    # Create new employee record with minimal info
                    await db.execute("""
                        INSERT INTO employees (id, name, department, role) 
                        VALUES (?, ?, ?, ?)
                    """, (employee_id, f"Employee {employee_id}", "Unknown", "Unknown"))
                
                # Update the interview session with employee ID
                await db.execute("""
                    UPDATE interview_sessions 
                    SET employee_id = ? 
                    WHERE id = ?
                """, (employee_id, current_session_id))
                
                await db.commit()
                logger.info(f"Updated session {current_session_id} with employee ID: {employee_id}")

    async def _process_events(self, session_id: str):
        logger.info(f"Starting event processing for session {session_id}")
        try:
            session = self.active_sessions.get(session_id)
            websocket = self.websockets.get(session_id)
            
            if not session or not websocket:
                logger.warning(f"Session or websocket not found for {session_id}")
                return

            async for event in session:
                # Check if session is still active before processing
                if session_id not in self.active_sessions or session_id not in self.websockets:
                    logger.info(f"Session {session_id} no longer active, stopping event processing")
                    break
                    
                try:
                    event_data = await self._serialize_event(event)
                    await websocket.send_text(json.dumps(event_data))
                except Exception as send_error:
                    logger.warning(f"Failed to send event to {session_id}: {send_error}")
                    # If we can't send, the connection is likely closed
                    break
                    
        except asyncio.CancelledError:
            logger.info(f"Event processing cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error processing events for session {session_id}: {e}", exc_info=True)
        finally:
            logger.info(f"Event processing ended for session {session_id}")

    async def _serialize_event(self, event: RealtimeSessionEvent) -> dict[str, Any]:
        base_event: dict[str, Any] = {
            "type": event.type,
        }

        if event.type == "agent_start":
            base_event["agent"] = event.agent.name
        elif event.type == "agent_end":
            base_event["agent"] = event.agent.name
        elif event.type == "handoff":
            base_event["from"] = event.from_agent.name
            base_event["to"] = event.to_agent.name
        elif event.type == "tool_start":
            base_event["tool"] = event.tool.name
        elif event.type == "tool_end":
            base_event["tool"] = event.tool.name
            base_event["output"] = str(event.output)
        elif event.type == "audio":
            base_event["audio"] = base64.b64encode(event.audio.data).decode("utf-8")
        elif event.type == "audio_interrupted":
            pass
        elif event.type == "audio_end":
            pass
        elif event.type == "history_updated":
            base_event["history"] = [item.model_dump(mode="json") for item in event.history]
        elif event.type == "history_added":
            pass
        elif event.type == "guardrail_tripped":
            base_event["guardrail_results"] = [
                {"name": result.guardrail.name} for result in event.guardrail_results
            ]
        elif event.type == "raw_model_event":
            base_event["raw_model_event"] = {
                "type": event.data.type,
            }
        elif event.type == "error":
            base_event["error"] = str(event.error) if hasattr(event, "error") else "Unknown error"
        else:
            assert_never(event)

        return base_event

manager = RealtimeWebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_database()
    logger.info("Database initialized")
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/api/query")
async def execute_query(request: QueryRequest):
    """Execute a SQL query on the interview database"""
    query = request.query.strip()
    
    # Basic security - only allow SELECT, PRAGMA table_info, and .schema equivalent
    query_upper = query.upper()
    allowed_commands = ['SELECT', 'WITH', 'PRAGMA TABLE_INFO']
    
    if not any(query_upper.startswith(cmd) for cmd in allowed_commands):
        raise HTTPException(
            status_code=400, 
            detail="Only SELECT queries and PRAGMA table_info are allowed for security reasons"
        )
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(query)
            results = await cursor.fetchall()
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            return {
                "results": results,
                "columns": columns,
                "count": len(results)
            }
            
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    logger.info(f"WebSocket connection request for session {session_id}")
    try:
        await manager.connect(websocket, session_id)
        logger.info(f"WebSocket connected for session {session_id}")
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "audio":
                # Convert int16 array to bytes
                int16_data = message["data"]
                audio_bytes = struct.pack(f"{len(int16_data)}h", *int16_data)
                await manager.send_audio(session_id, audio_bytes)
            elif message["type"] == "employee_id":
                # Update employee ID for the session
                employee_id = message.get("employee_id")
                if employee_id:
                    await manager.update_employee_id(session_id, employee_id)
                    logger.info(f"Employee ID {employee_id} set for session {session_id}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        await manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        await manager.disconnect(session_id)

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/database")
async def read_database():
    return FileResponse("static/database.html")

# Mount static files last to avoid route conflicts
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
