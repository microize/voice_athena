# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real-time voice-based SQL technical interview application with two main components:
1. **Python Voice Assistant** (`app/`): FastAPI server with OpenAI Realtime API integration for SQL interviews
2. **Next.js Frontend** (`openai-fm-main/`): Text-to-speech web application (separate project)

The primary focus is the Python voice assistant that conducts SQL technical interviews using OpenAI's Realtime API.

## Development Commands

### Python Voice Assistant (Primary Project)
Located in `app/` directory:

```bash
# Install dependencies
uv sync

# Alternative with pip
pip install fastapi uvicorn websockets openai-agents

# Start development server
uv run python server.py

# Direct python execution
python server.py
```

Server runs on http://localhost:8000

### Next.js Project (Secondary)
Located in `openai-fm-main/openai-fm-main/`:

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Architecture

### Voice Assistant (`app/`)
- **Entry Point**: `server.py` - FastAPI application with WebSocket endpoints
- **Agent System**: Uses `openai-agents` library with `RealtimeAgent` for SQL interview conduct
- **Session Management**: `RealtimeWebSocketManager` handles multiple concurrent interview sessions
- **Audio Processing**: Real-time audio capture/playback with 24kHz mono format
- **Frontend**: Vanilla JavaScript (`static/app.js`) with WebSocket communication

Key architectural patterns:
- WebSocket-based real-time communication (`/ws/{session_id}`)
- Event-driven agent system with tool integration
- Session isolation with unique session IDs
- Audio streaming with interruption handling

### Interview Flow
1. WebSocket connection establishes session
2. AI agent introduces itself and assesses candidate's SQL level
3. Progressive difficulty questions based on responses
4. Real-time feedback and hint system using function tools
5. Session cleanup on disconnect

## Environment Setup

Required environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Alternative: Create `.env` file in `app/` directory with the API key.

## Session Reporting System

The application includes comprehensive session tracking and reporting:

### Database Schema
- **SQLite database** (`interview_sessions.db`) with tables:
  - `employees`: Employee records with ID, name, department, role
  - `interview_sessions`: Session metadata with employee linking
  - `interview_questions`: Questions asked with difficulty/category tracking
  - `interview_responses`: Response evaluation with scores and timing
  - `session_reports`: Generated performance reports

### Function Tools
- `log_question_asked()`: Tracks questions by category (basic_queries, joins, window_functions, etc.) and difficulty (beginner, intermediate, advanced)
- `log_response_evaluation()`: Evaluates responses with 0.0-1.0 scoring and feedback
- `generate_session_report()`: Creates comprehensive report with strengths, weaknesses, and recommendations

### Agent Instructions
The SQL interviewer agent automatically:
1. Logs each question before asking using appropriate category/difficulty tags
2. Evaluates and scores each response (0.0-1.0 scale)
3. Generates a final session report with personalized recommendations
4. Ends the database session upon completion

### Frontend Features
- Employee ID input field for session tracking
- Enhanced message formatting for session reports
- Structured display of performance metrics and recommendations

## Key Dependencies
- **Python**: FastAPI, uvicorn, websockets, openai-agents, aiosqlite
- **JavaScript**: Next.js, React, TypeScript, Tailwind CSS
- **Database**: SQLite with async support (aiosqlite)
- **Audio**: WebAudio API for real-time processing

## Development Notes
- Python project requires Python 3.12+
- OpenAI Realtime API requires paid account with beta access
- Audio capture requires HTTPS or localhost for browser permissions
- Session management prevents memory leaks through proper cleanup
- Database automatically initializes on first startup
- Employee ID is optional - sessions work without it but won't be tracked long-term