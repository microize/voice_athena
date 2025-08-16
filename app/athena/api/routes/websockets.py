"""WebSocket routes for real-time communication with OpenAI Realtime API"""
import json
import struct
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from athena.agents import RealtimeSession, AGENTS_AVAILABLE
from athena.services.interview_agent_service import InterviewAgentService, current_session_id
from athena.core.dependencies import get_interview_agent_service

router = APIRouter(tags=["websockets"])
logger = logging.getLogger(__name__)

class RealtimeWebSocketManager:
    """Enhanced WebSocket manager with OpenAI Realtime API integration"""
    
    def __init__(self):
        if AGENTS_AVAILABLE:
            self.active_sessions: Dict[str, RealtimeSession] = {}
        else:
            self.active_sessions: Dict[str, Any] = {}
        self.session_contexts: Dict[str, Any] = {}
        self.websockets: Dict[str, WebSocket] = {}
        self.event_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection and create realtime session"""
        logger.info(f"Accepting WebSocket connection for session {session_id}")
        await websocket.accept()
        self.websockets[session_id] = websocket

        try:
            # Get interview agent service
            agent_service = get_interview_agent_service()
            
            if AGENTS_AVAILABLE:
                logger.info(f"Creating RealtimeSession for session {session_id}")
                
                # Create realtime session with OpenAI
                session, session_context = await agent_service.create_realtime_session(session_id)
                
                if session and session_context:
                    self.active_sessions[session_id] = session
                    self.session_contexts[session_id] = session_context
                    logger.info(f"Realtime session created for {session_id}")

                    # Start event processing task
                    task = asyncio.create_task(self._process_events(session_id))
                    self.event_tasks[session_id] = task
                    logger.info(f"Event processing task started for {session_id}")
                else:
                    logger.error(f"Failed to create realtime session for {session_id}")
                    raise Exception("Failed to create realtime session")
            else:
                # Basic WebSocket mode without agents
                logger.info(f"WebSocket connected in basic mode for session {session_id}")
                self.active_sessions[session_id] = {"basic_mode": True}
                
                # Send welcome message
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "content": "WebSocket connected! Agents module not available - running in basic mode."
                }))
                
        except Exception as e:
            logger.error(f"Error creating session for {session_id}: {e}", exc_info=True)
            raise

    async def disconnect(self, session_id: str):
        """Clean up WebSocket connection and realtime session"""
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

    async def send_message(self, session_id: str, message: str):
        """Send message to specific session"""
        if session_id in self.websockets:
            websocket = self.websockets[session_id]
            await websocket.send_text(message)
    
    async def send_audio(self, session_id: str, audio_bytes: bytes):
        """Send audio data to OpenAI Realtime API"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if hasattr(session, 'send_audio'):
                await session.send_audio(audio_bytes)
            else:
                # Basic mode - just echo back
                if session_id in self.websockets:
                    websocket = self.websockets[session_id]
                    await websocket.send_bytes(audio_bytes)

    async def _process_events(self, session_id: str):
        """Process events from OpenAI Realtime API and send to client"""
        logger.info(f"Starting event processing for session {session_id}")
        try:
            session = self.active_sessions.get(session_id)
            websocket = self.websockets.get(session_id)
            
            if not session or not websocket:
                logger.warning(f"Session or websocket not found for {session_id}")
                return

            # Check if this is a basic mode session
            if isinstance(session, dict) and session.get("basic_mode"):
                logger.info(f"Session {session_id} is in basic mode, no event processing needed")
                return

            if AGENTS_AVAILABLE:
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

    async def _serialize_event(self, event) -> Dict[str, Any]:
        """Convert realtime event to JSON-serializable format"""
        try:
            # Use the same serialization pattern as the original server.py.backup
            base_event = {
                "type": event.type,
                "timestamp": asyncio.get_event_loop().time()
            }

            # Handle specific event types based on the original implementation
            if event.type == "agent_start":
                base_event["agent"] = event.agent.name if hasattr(event, 'agent') and hasattr(event.agent, 'name') else "unknown"
            elif event.type == "agent_end":
                base_event["agent"] = event.agent.name if hasattr(event, 'agent') and hasattr(event.agent, 'name') else "unknown"
            elif event.type == "handoff":
                base_event["from"] = event.from_agent.name if hasattr(event, 'from_agent') and hasattr(event.from_agent, 'name') else "unknown"
                base_event["to"] = event.to_agent.name if hasattr(event, 'to_agent') and hasattr(event.to_agent, 'name') else "unknown"
            elif event.type == "tool_start":
                base_event["tool"] = event.tool.name if hasattr(event, 'tool') and hasattr(event.tool, 'name') else "unknown"
            elif event.type == "tool_end":
                base_event["tool"] = event.tool.name if hasattr(event, 'tool') and hasattr(event.tool, 'name') else "unknown"
                base_event["output"] = str(event.output) if hasattr(event, 'output') else ""
            elif event.type == "audio":
                if hasattr(event, 'audio') and hasattr(event.audio, 'data'):
                    import base64
                    base_event["audio"] = base64.b64encode(event.audio.data).decode("utf-8")
                else:
                    base_event["audio"] = ""
            elif event.type == "audio_interrupted":
                pass  # No additional data needed
            elif event.type == "audio_end":
                pass  # No additional data needed
            elif event.type == "history_updated":
                if hasattr(event, 'history') and event.history:
                    base_event["history"] = [item.model_dump(mode="json") for item in event.history]
                else:
                    base_event["history"] = []
            elif event.type == "history_added":
                pass  # No additional data needed
            elif event.type == "guardrail_tripped":
                if hasattr(event, 'guardrail_results'):
                    base_event["guardrail_results"] = [
                        {"name": result.guardrail.name} for result in event.guardrail_results
                    ]
                else:
                    base_event["guardrail_results"] = []
            elif event.type == "raw_model_event":
                base_event["raw_model_event"] = {
                    "type": event.data.type if hasattr(event, 'data') and hasattr(event.data, 'type') else "unknown",
                }
            elif event.type == "error":
                base_event["error"] = str(event.error) if hasattr(event, "error") else "Unknown error"
            else:
                # For any other event types, try to include basic data
                if hasattr(event, 'data'):
                    base_event["data"] = event.data
                elif hasattr(event, 'content'):
                    base_event["content"] = event.content
                
            return base_event
                
        except Exception as e:
            logger.error(f"Error serializing event: {e}")
            return {
                "type": "error",
                "message": f"Failed to serialize event: {e}",
                "timestamp": asyncio.get_event_loop().time()
            }

# Global WebSocket manager instance
manager = RealtimeWebSocketManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time interview sessions with OpenAI integration"""
    logger.info(f"WebSocket connection request for session {session_id}")
    
    try:
        await manager.connect(websocket, session_id)
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "audio":
                # Convert int16 array to bytes for audio processing
                int16_data = message.get("data", [])
                audio_bytes = struct.pack(f"{len(int16_data)}h", *int16_data)
                await manager.send_audio(session_id, audio_bytes)
            
            elif message.get("type") == "text":
                # For text messages, we could send them to OpenAI as well
                # For now, just log them
                logger.info(f"Text message from {session_id}: {message.get('content', '')}")
            
            else:
                # Unknown message type
                logger.warning(f"Unknown message type from {session_id}: {message.get('type')}")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        await manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}", exc_info=True)
        await manager.disconnect(session_id)