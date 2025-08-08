# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real-time voice-based SQL technical interview application with two main components:
1. **Python Voice Assistant** (`app/`): FastAPI server with OpenAI Realtime API integration for SQL interviews

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
1. Employee enters ID and submits for session tracking
2. WebSocket connection establishes session with employee linking
3. Concise SQL interviewer asks intermediate/advanced questions only
4. Real-time response evaluation with 0.0-1.0 scoring
5. 4-6 questions total with immediate feedback
6. Final session report generated automatically
7. Session cleanup on disconnect

## Environment Setup

Create a `.env` file in the `app/` directory:
```bash
cp .env.example .env
```

Then edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your-actual-openai-api-key-here
```

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
- **Main Interface** (`/`): Employee ID input → Submit → Connect → Voice Interview
- **Database Interface** (`/database`): Web-based SQL query tool for data analysis
- Employee ID validation and session flow control
- Enhanced message formatting for session reports
- Structured display of performance metrics and recommendations

## Key Dependencies
- **Python**: FastAPI, uvicorn, websockets, openai-agents, aiosqlite
- **JavaScript**: Next.js, React, TypeScript, Tailwind CSS
- **Database**: SQLite with async support (aiosqlite)
- **Audio**: WebAudio API for real-time processing

## Application URLs

- **Main Interview Interface**: `http://localhost:8000/` - Voice-based SQL interviews
- **Database Query Interface**: `http://localhost:8000/database` - SQL analytics and reporting
- **WebSocket Endpoint**: `/ws/{session_id}` - Real-time communication
- **Query API**: `/api/query` - Execute SQL queries (POST)

## Agent Configuration

The SQL interviewer agent is configured for:
- **Concise behavior**: Responses under 2 sentences, no small talk
- **Technical focus**: Only intermediate/advanced SQL questions
- **Question categories**: joins, subqueries, window_functions, cte, performance, indexing, query_optimization
- **Automatic logging**: Every question and response tracked
- **Scoring system**: 0.0-1.0 scale with immediate feedback

## Development Notes
- Python project requires Python 3.12+
- OpenAI Realtime API requires paid account with beta access
- Audio capture requires HTTPS or localhost for browser permissions
- Session management prevents memory leaks through proper cleanup
- Database automatically initializes on first startup
- Employee ID is required - sessions are tracked by employee for analytics
- Database interface provides read-only access for security