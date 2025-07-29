import asyncio
import base64
import json
import logging
import struct
from contextlib import asynccontextmanager
from typing import Any, assert_never

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agents import function_tool
from agents.realtime import RealtimeAgent, RealtimeRunner, RealtimeSession, RealtimeSessionEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@function_tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."


@function_tool
def get_secret_number() -> int:
    """Returns the secret number, if the user asks for it."""
    return 71


haiku_agent = RealtimeAgent(
    name="Haiku Agent",
    instructions="You are a haiku poet. You must respond ONLY in traditional haiku format (5-7-5 syllables). Every response should be a proper haiku about the topic. Do not break character.",
    tools=[],
)

agent = RealtimeAgent(
    name="Assistant",
    instructions="You are an English-speaking assistant. Always respond in clear, natural English. Speak at a moderate pace for good user experience. If the user wants poetry or haikus, you can hand them off to the haiku agent via the transfer_to_haiku_agent tool.",
    tools=[get_weather, get_secret_number],
    handoffs=[haiku_agent],
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
            logger.info(f"Creating RealtimeRunner for session {session_id}")
            runner = RealtimeRunner(agent)
            
            # Configure model settings for English language and appropriate voice
            model_config = {
                "voice": "alloy",  # English-speaking voice
                "input_audio_transcription": {
                    "model": "gpt-4o-mini-transcribe",
                    "language": "en"  # Explicitly set English for transcription
                }
            }
            
            session_context = await runner.run(model_config=model_config)
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
    yield


app = FastAPI(lifespan=lifespan)


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

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        await manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        await manager.disconnect(session_id)


app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
