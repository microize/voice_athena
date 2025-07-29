# Realtime Demo App

A web-based realtime voice assistant demo with a FastAPI backend and HTML/JS frontend.

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
   uv add fastapi uvicorn websockets openai-agents
   ```

## Setup

1. Set your OpenAI API key as an environment variable:
   ```powershell
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key-here"
   ```
   ```bash
   # Linux/Mac
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Verify your API key works:
   ```powershell
   # Windows PowerShell
   Invoke-RestMethod -Uri "https://api.openai.com/v1/models" -Headers @{"Authorization"="Bearer $env:OPENAI_API_KEY"}
   ```

## Usage

Start the application:

```bash
uv run python server.py
```

Then open your browser to: http://localhost:8000

## How to Use

1. Click **Connect** to establish a realtime session
2. Audio capture starts automatically - just speak naturally
3. Click the **Mic On/Off** button to mute/unmute your microphone
4. Watch the conversation unfold in the left pane
5. Monitor raw events in the right pane (click to expand/collapse)
6. Click **Disconnect** when done

## Architecture

-   **Backend**: FastAPI server with WebSocket connections for real-time communication
-   **Session Management**: Each connection gets a unique session with the OpenAI Realtime API
-   **Audio Processing**: 24kHz mono audio capture and playback
-   **Event Handling**: Full event stream processing with transcript generation
-   **Frontend**: Vanilla JavaScript with clean, responsive CSS

The demo showcases the core patterns for building realtime voice applications with the OpenAI Agents SDK.
