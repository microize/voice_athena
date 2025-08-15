# Athena - SQL Technical Interview Assistant

A real-time voice-based SQL technical interview application with comprehensive employee tracking and database analytics.

## Features

- **Voice-based SQL interviews** with real-time AI feedback
- **Employee ID tracking** for session management
- **Comprehensive database analytics** with web-based query interface
- **Performance scoring** and detailed session reports
- **Question categorization** by difficulty (intermediate/advanced) and topic
- **SQLite database** with complete audit trail

## Prerequisites

- **OpenAI API Key**: You need a valid OpenAI API key with access to the Realtime API
- **uv package manager**: Install from https://astral.sh/uv/install.ps1 (Windows) or https://astral.sh/uv/install.sh (Linux/Mac)

## Installation

1. Install uv if not already installed:
   ```powershell
   # Windows PowerShell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Initialize the project and install dependencies:
   ```bash
   uv init
   uv add fastapi uvicorn websockets openai-agents aiosqlite
   ```

## Setup

1. Create a `.env` file in the `app/` directory and add your OpenAI API key:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```
   
   Then edit `.env` and replace the placeholder with your actual API key:
   ```
   OPENAI_API_KEY=your-actual-openai-api-key-here
   ```

2. Verify your API key works:
   ```bash
   # Test with curl (replace with your actual key)
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer your-actual-openai-api-key-here"
   ```

## Usage

Start the application:

```bash
uv run python server.py
```

The application provides two main interfaces:

### **1. SQL Interview Interface**
Access at: http://localhost:8000

**Interview Flow:**
1. Enter your **Employee ID** in the left panel and click **Submit**
2. Click **Connect** to establish a realtime session (button enabled after Employee ID submission)
3. Audio capture starts automatically - speak naturally to begin your SQL interview
4. The AI interviewer will ask intermediate/advanced SQL questions
5. Receive real-time feedback and scoring on your responses
6. Complete 4-6 questions for a full session report
7. Click **Disconnect** when done

### **2. Database Query Interface**
Access at: http://localhost:8000/database

**Query Features:**
- Execute SQL SELECT queries on the interview database
- View session data, employee performance, and question analytics
- Sample queries provided for common analysis tasks
- Real-time results with sortable tables
- Security-protected (read-only access)

## Architecture

### **Backend Components:**
- **FastAPI server** with WebSocket connections for real-time communication
- **SQL Interview Agent** with concise, technical interviewing behavior
- **SQLite database** with comprehensive session tracking and employee management
- **Function tools** for question logging, response evaluation, and report generation
- **RESTful API** for database querying and analytics

### **Frontend Components:**
- **Interview Interface** (`static/index.html`) - Voice-based SQL interviews with employee ID tracking
- **Database Interface** (`static/database.html`) - Web-based SQL query tool for data analysis
- **Vanilla JavaScript** with WebSocket communication and responsive CSS

### **Database Schema:**
- `employees` - Employee records and metadata
- `interview_sessions` - Session tracking with employee linking
- `interview_questions` - Question categorization and difficulty tracking
- `interview_responses` - Response evaluation with scoring and feedback
- `session_reports` - Comprehensive performance reports

### **Agent Behavior:**
- **Concise responses** (under 2 sentences)
- **Intermediate/Advanced focus** - No basic SQL questions
- **Technical categories**: joins, subqueries, window_functions, CTEs, performance optimization
- **Real-time evaluation** with 0.0-1.0 scoring scale

## Sample Database Queries

```sql
-- View recent interview sessions
SELECT * FROM interview_sessions ORDER BY start_time DESC LIMIT 10;

-- Employee performance summary  
SELECT employee_id, COUNT(*) as sessions, AVG(overall_score) as avg_score
FROM interview_sessions 
WHERE employee_id IS NOT NULL 
GROUP BY employee_id;

-- Question difficulty distribution
SELECT category, difficulty, COUNT(*) as count
FROM interview_questions 
GROUP BY category, difficulty;
```

## Development Notes

- **Python 3.12+** required
- **OpenAI Realtime API** requires paid account with beta access
- **HTTPS/localhost** required for browser microphone permissions
- **Database auto-initialization** on first startup
- **Employee ID tracking** maintains session history and analytics
