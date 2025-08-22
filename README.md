# Athena - Voice-Based SQL Interview Platform

**Athena** is a sophisticated real-time voice-based SQL technical interview application built with modern web technologies. The platform conducts AI-powered SQL interviews using OpenAI's Realtime API with comprehensive session tracking, performance analytics, and modular frontend architecture.

## 🚀 Features

### **Core Functionality**
- **Real-time Voice Interviews**: AI-powered SQL interviews with OpenAI Realtime API
- **Comprehensive Analytics**: Employee tracking, performance scoring, and detailed reports
- **Multi-interface Platform**: Voice interviews, database analytics, coding challenges, and dashboard
- **Security-First Design**: Input validation, authentication, rate limiting, and secure sessions
- **Modular Architecture**: Component-based frontend with clean separation of concerns

### **Interview System**
- **Intelligent Question Selection**: Intermediate/advanced SQL focus with categorized questions
- **Real-time Evaluation**: 0.0-1.0 scoring with immediate feedback
- **Session Management**: Employee ID tracking with complete audit trails
- **Performance Reports**: Comprehensive analytics with strengths/weaknesses analysis

### **Database Analytics**
- **Web-based Query Interface**: Execute SQL queries with real-time results
- **Security-Protected**: Read-only access with SQL injection prevention
- **Performance Insights**: Employee analytics and question difficulty tracking

## 🛠️ Technology Stack

### **Backend**
- **Framework**: Python 3.12+ with FastAPI
- **Real-time Communication**: WebSockets + OpenAI Realtime API
- **Database**: SQLite with aiosqlite for async operations
- **Security**: Bcrypt, rate limiting, CSP headers, input validation
- **Package Management**: UV for Python dependencies

### **Frontend**
- **Architecture**: Modular component-based design
- **JavaScript**: Vanilla JS with shared utilities and component isolation
- **Styling**: Modular CSS with CSS variables and PostCSS
- **Components**: Self-contained .html/.css/.js modules
- **Security**: Client-side input sanitization and XSS prevention

### **Infrastructure**
- **Session Management**: Secure cookies with HTTPOnly flags
- **Audio Processing**: 24kHz mono format with interruption handling
- **Database Schema**: Comprehensive tracking with employees, sessions, questions, responses

## 📁 Project Structure

```
athena/
├── app/                          # Main application directory
│   ├── athena/                   # Core application package
│   │   ├── __init__.py          # Package initialization
│   │   ├── main.py              # Application entry point and uvicorn server
│   │   ├── agents/              # AI agent system integration
│   │   │   └── __init__.py      # OpenAI Realtime API agent exports
│   │   ├── api/                 # FastAPI route definitions
│   │   │   ├── __init__.py      # API router factory
│   │   │   └── routes/          # Individual route modules
│   │   │       ├── __init__.py  # Route imports
│   │   │       ├── auth.py      # Login/logout/registration endpoints
│   │   │       ├── database.py  # SQL query execution API
│   │   │       ├── interview.py # Interview session management
│   │   │       ├── pages.py     # HTML page serving endpoints
│   │   │       ├── problems.py  # Coding problem CRUD operations
│   │   │       ├── user.py      # User profile and progress tracking
│   │   │       └── websockets.py # WebSocket connection handlers
│   │   ├── core/                # Core application framework
│   │   │   ├── __init__.py      # Core module exports
│   │   │   ├── app.py           # FastAPI application factory
│   │   │   ├── config.py        # Environment configuration management
│   │   │   ├── database.py      # SQLite database initialization
│   │   │   ├── dependencies.py  # Dependency injection providers
│   │   │   ├── exceptions.py    # Custom exception classes
│   │   │   ├── logging_config.py # Structured logging setup
│   │   │   ├── middleware.py    # Security headers and request logging
│   │   │   └── security.py      # Authentication, rate limiting, password hashing
│   │   ├── models/              # Data models and validation
│   │   │   ├── __init__.py      # Model exports
│   │   │   └── schemas.py       # Pydantic validation models
│   │   ├── services/            # Business logic layer
│   │   │   ├── __init__.py      # Service exports
│   │   │   ├── interview_agent_service.py # OpenAI Realtime API integration
│   │   │   ├── interview_service.py # Interview session orchestration
│   │   │   ├── judge0_service.py # Code execution via Judge0 API
│   │   │   ├── problem_service.py # Coding problem management
│   │   │   └── user_service.py  # User management and analytics
│   │   └── utils/               # Shared utility functions
│   │       └── __init__.py      # Utility exports
│   ├── static/                  # Frontend assets (modular architecture)
│   │   ├── components/          # Reusable UI components
│   │   │   ├── nav-component.html # Navigation component template
│   │   │   ├── nav-component.js   # Navigation component logic
│   │   │   └── nav-component.css  # Navigation component styles
│   │   ├── styles/              # Modular CSS organization
│   │   │   ├── global.css       # CSS variables, fonts, common layouts
│   │   │   ├── buttons.css      # All button variants and states
│   │   │   ├── interview.css    # Voice interview interface styles
│   │   │   ├── database.css     # SQL query interface styles
│   │   │   ├── dashboard.css    # Dashboard overview styles
│   │   │   ├── login.css        # Authentication page styles
│   │   │   ├── problems.css     # Coding problems interface styles
│   │   │   └── modal.css        # Modal dialog styles
│   │   ├── styles-new/          # Advanced CSS module system
│   │   │   ├── 01-settings/     # CSS custom properties and variables
│   │   │   ├── 02-tools/        # Utility classes and mixins
│   │   │   ├── 03-generic/      # CSS reset and normalization
│   │   │   ├── 04-elements/     # Base element styling
│   │   │   ├── 05-objects/      # Layout and structural components
│   │   │   ├── 06-components/   # UI component styles
│   │   │   ├── 07-pages/        # Page-specific styles
│   │   │   └── main.css         # Main stylesheet orchestration
│   │   ├── js/                  # Modular JavaScript architecture
│   │   │   ├── utils.js         # Shared utilities (sanitization, messaging)
│   │   │   ├── interview.js     # Voice interview WebSocket logic
│   │   │   ├── database.js      # SQL query interface and results
│   │   │   ├── login.js         # Authentication form handling
│   │   │   ├── problem.js       # Individual problem view and editor
│   │   │   ├── problems.js      # Problem list and filtering
│   │   │   └── lucide.js        # Icon library integration
│   │   ├── assets/              # Static media files
│   │   │   ├── athena-demo.mp4  # Application demo video
│   │   │   └── *.png            # Application screenshots and images
│   │   ├── *.html               # Page templates
│   │   │   ├── index.html       # Voice interview interface
│   │   │   ├── login.html       # Authentication page
│   │   │   ├── dashboard.html   # User dashboard
│   │   │   ├── database.html    # SQL query interface
│   │   │   ├── problems.html    # Problem list view
│   │   │   ├── problem.html     # Individual problem view
│   │   │   └── test-*.html      # Development testing pages
│   │   ├── app.js               # Legacy application entry point
│   │   ├── audio-processor-worklet.js # WebAudio worklet for voice processing
│   │   ├── favicon.ico          # Application favicon
│   │   └── favicon.svg          # SVG favicon
│   ├── data/                    # Application data storage
│   │   └── interview_sessions.db # SQLite database file
│   ├── docs/                    # Additional documentation
│   │   ├── ARCHITECTURE.md      # System architecture documentation
│   │   ├── INTERVIEW_FIXES.md   # Interview system troubleshooting
│   │   └── SETUP_CODING_PLATFORM.md # Platform setup guide
│   ├── logs/                    # Application logs
│   │   ├── athena.log           # General application logs
│   │   └── athena_errors.log    # Error-specific logs
│   ├── scripts/                 # Database and maintenance scripts
│   │   ├── add_sql_problems.py  # Seed database with SQL practice problems
│   │   ├── create_favicon.py    # Generate application favicon
│   │   ├── final_sql_schema_update.py # Schema migration script
│   │   ├── fix_sql_solutions.py # Repair problem solutions
│   │   ├── update_all_sql_schemas.py # Batch schema updates
│   │   └── update_sql_schemas.py # Individual schema updates
│   ├── tests/                   # Test suite
│   │   └── __init__.py          # Test package initialization
│   ├── pyproject.toml           # Python dependencies and project configuration
│   ├── uv.lock                  # Locked dependency versions for reproducible builds
│   ├── run_athena.py            # Alternative application runner
│   ├── .env                     # Environment variables (not in version control)
│   ├── CLAUDE.md                # AI assistant development guide
│   └── SECURITY.md              # Security documentation and best practices
├── CLAUDE.md                    # Repository-level AI assistant guide
├── CONTRIBUTING.md              # Contribution guidelines
├── PROJECT_STRUCTURE.md         # Detailed project structure documentation
├── REPOSITORY_GUIDE.md          # Repository navigation guide
└── README.md                    # Project documentation (this file)
```

## 🔧 Installation & Setup

### **Prerequisites**
- **Python 3.12+**
- **UV Package Manager**: Install from [astral.sh/uv](https://astral.sh/uv)
- **OpenAI API Key**: Realtime API access required

### **Installation Steps**

1. **Install UV package manager**:
   ```bash
   # Windows PowerShell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Navigate to project directory**:
   ```bash
   cd app/
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Configure environment**:
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your-actual-openai-api-key-here
   ```

5. **Verify OpenAI API access**:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer your-actual-openai-api-key-here"
   ```

6. **Start the application**:
   ```bash
   uv run python server.py
   ```

**Server runs on**: http://localhost:8000

## 🎯 Application Interfaces

### **1. Voice Interview Interface** (`/`)
**Primary interview experience with real-time AI interaction**

**Workflow**:
1. **Employee Authentication**: Enter Employee ID and submit
2. **Session Connection**: Click "Connect" to establish WebSocket session
3. **Voice Interview**: Speak naturally - AI asks intermediate/advanced SQL questions
4. **Real-time Feedback**: Receive immediate scoring and evaluation
5. **Session Completion**: 4-6 questions with comprehensive performance report
6. **Session Cleanup**: Click "Disconnect" to end session

**Features**:
- Real-time audio processing (24kHz mono)
- Session isolation with unique session IDs
- Employee ID validation and tracking
- Help modal with usage instructions

### **2. Database Analytics Interface** (`/database`)
**Web-based SQL query tool for data analysis and reporting**

**Capabilities**:
- Execute SQL SELECT queries on interview database
- View employee performance metrics and session history
- Analyze question difficulty distributions and response patterns
- Export results for further analysis
- Security-protected with read-only access

**Sample Queries**:
```sql
-- Recent interview sessions
SELECT * FROM interview_sessions ORDER BY start_time DESC LIMIT 10;

-- Employee performance summary
SELECT employee_id, COUNT(*) as sessions, AVG(overall_score) as avg_score
FROM interview_sessions 
WHERE employee_id IS NOT NULL 
GROUP BY employee_id;

-- Question category analysis
SELECT category, difficulty, COUNT(*) as count
FROM interview_questions 
GROUP BY category, difficulty;
```

### **3. Dashboard Interface** (`/dashboard`)
**Performance overview and quick navigation hub**

**Features**:
- User progress tracking and statistics
- Recent activity monitoring
- Quick links to all platform features
- Performance metrics and visual indicators

### **4. Coding Problems Interface** (`/problems`)
**Supplementary coding challenges for comprehensive assessment**

**Features**:
- Curated programming problems with difficulty filters
- Code editor with syntax highlighting
- Test case validation and feedback
- Performance analytics and submission tracking

### **5. Authentication System** (`/login`)
**Secure user authentication with multiple options**

**Security Features**:
- Bcrypt password hashing (12 rounds)
- Rate limiting on authentication endpoints
- Input sanitization and validation
- Social login integration support

## 🏗️ Modular Frontend Architecture

### **Component-Based Design**
The frontend follows strict modular principles with clear separation of concerns:

**Global Styles** (`styles/global.css`):
- CSS custom properties (variables)
- Font imports via `@import`
- Common layout classes (`.container`, `.main-content`)
- Base typography and reset styles
- Status colors (`--success`, `--error`, `--warning`)

**Component Styles**:
- **buttons.css**: All button variants (`.button`, `.action-btn`, mic buttons)
- **nav-component.css**: Navigation-specific styles
- **Page-specific CSS**: Only styles unique to that page

**JavaScript Modules**:
- **utils.js**: Shared utilities (`loadNavigation`, `sanitizeInput`, `showMessage`)
- **Component JS**: Self-contained functionality for specific features
- **Page JS**: Only logic specific to that page

### **Security Integration**
```javascript
// Input sanitization (utils.js)
function sanitizeInput(input) {
    return input.trim().slice(0, 50).replace(/[<>&"']/g, '');
}

// Proper dependency loading order
<script src="/static/components/nav-component.js"></script>
<script src="/static/js/utils.js"></script>
<script src="/static/js/page-specific.js"></script>
```

## 🛡️ Security Architecture

### **Input Validation & SQL Security**
```python
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    
    @validator('query')
    def validate_sql_query(cls, v):
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER']
        for keyword in dangerous_keywords:
            if keyword in v.upper():
                raise ValueError(f'Operation "{keyword}" is not allowed')
        return v
```

### **Authentication & Session Management**
- **Bcrypt Password Hashing**: 12-round salting for secure password storage
- **Secure Session Cookies**: HTTPOnly, Secure, SameSite protections
- **Rate Limiting**: 5 attempts per 15 minutes on authentication endpoints
- **CSRF Protection**: State-changing operations protected

### **Security Headers**
- **Content Security Policy (CSP)**: Strict resource loading policies
- **HSTS**: Force HTTPS connections
- **X-Frame-Options**: Prevent clickjacking
- **X-Content-Type-Options**: Prevent MIME type sniffing

## 🔌 API Documentation

### **Authentication Endpoints** (`/api/auth/`)
- `POST /api/auth/login` - User authentication with rate limiting
- `POST /api/auth/logout` - Session termination
- `POST /api/auth/register` - New user registration (if enabled)
- `GET /api/auth/verify` - Session validation

### **Interview Management** (`/api/interview/`)
- `POST /api/start-interview` - Initialize new interview session
- `GET /api/user/progress` - Retrieve user performance analytics
- `WebSocket /ws/{session_id}` - Real-time interview communication

### **Database Operations** (`/api/database/`)
- `POST /api/query` - Execute SQL SELECT queries with validation
- `GET /api/database/schema` - Retrieve database schema information

### **Problem Management** (`/api/problems/`)
- `GET /api/problems` - List coding problems with filtering
- `GET /api/problems/{problem_id}` - Get specific problem details
- `POST /api/problems/{problem_id}/submit` - Submit code solution
- `GET /api/problems/{problem_id}/submissions` - View submission history

### **User Management** (`/api/user/`)
- `GET /api/user/profile` - User profile information
- `PUT /api/user/profile` - Update user profile
- `GET /api/user/statistics` - Performance statistics and analytics

### **Page Serving** (`/`)
- `GET /` - Voice interview interface
- `GET /login` - Authentication page
- `GET /dashboard` - User dashboard
- `GET /database` - SQL query interface
- `GET /problems` - Problem list view
- `GET /problems/{problem_id}` - Individual problem view

## 📊 Database Schema

### **Core Tables**
```sql
-- Employee records for interview tracking
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    employee_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT,
    role TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interview session metadata
CREATE TABLE interview_sessions (
    id TEXT PRIMARY KEY,
    employee_id TEXT,
    username TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    overall_score REAL,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
);

-- Interview questions with categorization
CREATE TABLE interview_questions (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    category TEXT NOT NULL,  -- 'joins', 'window_functions', 'cte', etc.
    difficulty TEXT NOT NULL, -- 'beginner', 'intermediate', 'advanced'
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES interview_sessions (id)
);

-- Response evaluation and scoring
CREATE TABLE interview_responses (
    id INTEGER PRIMARY KEY,
    question_id INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    score REAL NOT NULL CHECK (score >= 0.0 AND score <= 1.0),
    feedback TEXT,
    response_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES interview_questions (id)
);

-- Comprehensive performance reports
CREATE TABLE session_reports (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    overall_score REAL,
    strengths TEXT,
    weaknesses TEXT,
    recommendations TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES interview_sessions (id)
);

-- Coding problems for supplementary assessment
CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    category TEXT NOT NULL,
    solution TEXT,
    test_cases TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User submissions and solutions
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    code TEXT NOT NULL,
    language TEXT NOT NULL,
    status TEXT, -- 'passed', 'failed', 'timeout'
    execution_time REAL,
    memory_usage INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems (id)
);
```

### **Agent Function Tools**
- `log_question_asked(question, category, difficulty)`: Track interview questions by category and difficulty
- `log_response_evaluation(response, score, feedback)`: Real-time response scoring (0.0-1.0 scale)
- `generate_session_report()`: Comprehensive performance analysis with strengths/weaknesses

## 🔍 Development & Testing

### **Quality Assurance**
```bash
# Run tests
uv run pytest

# Security scanning
uv run bandit -r athena/

# Code formatting
uv run black athena/
uv run isort athena/

# Type checking
uv run mypy athena/
```

### **Code Review Standards**
**Security Checklist**:
- [ ] No hardcoded credentials or API keys
- [ ] All inputs validated (frontend AND backend)
- [ ] SQL injection prevention implemented
- [ ] Authentication required for protected routes
- [ ] Rate limiting on sensitive endpoints
- [ ] Security headers configured

**Modular Architecture Checklist**:
- [ ] No duplicate CSS rules across files
- [ ] JavaScript utilities in utils.js
- [ ] CSS variables in global.css
- [ ] Component styles self-contained
- [ ] No inline styles or scripts
- [ ] Proper dependency loading order

## 🔧 Troubleshooting

### **Common Issues and Solutions**

#### **1. OpenAI API Connection Issues**
```bash
# Verify API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check environment variable
echo $OPENAI_API_KEY

# Verify .env file
cat app/.env | grep OPENAI_API_KEY
```

#### **2. Database Connection Problems**
```bash
# Check database file permissions
ls -la app/data/interview_sessions.db

# Test database connection
cd app && python -c "import aiosqlite; print('SQLite available')"

# Reset database (WARNING: destroys data)
rm app/data/interview_sessions.db
# Restart application to recreate
```

#### **3. WebSocket Connection Failures**
- **Check browser permissions**: Allow microphone access in browser settings
- **Verify HTTPS**: WebRTC requires secure context (HTTPS or localhost)
- **Firewall settings**: Ensure port 8000 is accessible
- **Browser compatibility**: Use Chrome/Firefox for best WebRTC support

#### **4. Audio Processing Issues**
```bash
# Check audio worklet file
ls -la app/static/audio-processor-worklet.js

# Verify sample rate support
# Browser console: navigator.mediaDevices.getSupportedConstraints()
```

#### **5. Rate Limiting Errors**
```bash
# Check current rate limits in logs
tail -f app/logs/athena.log | grep "rate_limit"

# Reset rate limiting (temporary)
# Edit config.py and restart application
```

### **Debug Mode Setup**
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start with verbose logging
cd app && uv run python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from athena.main import main
main()
"
```

### **Performance Monitoring**
```bash
# Monitor WebSocket connections
netstat -an | grep :8000

# Check memory usage
ps aux | grep python

# Monitor database locks
sqlite3 app/data/interview_sessions.db ".timeout 1000"
```

## 🚀 Deployment

### **Environment Configuration**
```bash
# Production environment
DEBUG=false
SESSION_SECRET_KEY=$(openssl rand -hex 32)
ADMIN_PASSWORD=secure-password
DATABASE_URL=sqlite:///interview_sessions.db
OPENAI_API_KEY=your-production-api-key
JUDGE0_API_KEY=your-judge0-api-key

# Optional: Rate limiting configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_WINDOW=900
```

### **Security Hardening**
```bash
# Database permissions
chmod 600 interview_sessions.db
chown app:app interview_sessions.db

# Application permissions
chown -R app:app /path/to/athena
chmod -R 755 /path/to/athena
chmod 600 /path/to/athena/app/.env

# Server configuration
# HTTPS only, secure headers, rate limiting enabled
# Configure reverse proxy (nginx/apache) with SSL termination
```

### **Systemd Service (Linux)**
```ini
# /etc/systemd/system/athena.service
[Unit]
Description=Athena Voice Interview Platform
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/path/to/athena/app
Environment=PATH=/path/to/athena/app/.venv/bin
ExecStart=/path/to/athena/app/.venv/bin/python athena/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### **Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY app/ .

# Install UV package manager
RUN pip install uv
RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "python", "athena/main.py"]
```

## 📈 Performance & Monitoring

### **Optimization Features**
- **Async/await**: All I/O operations for non-blocking performance
- **Modular Loading**: Efficient CSS/JS loading with component isolation
- **Connection Pooling**: Optimized database connections
- **WebSocket Management**: Efficient real-time communication

### **Monitoring Capabilities**
- Application performance tracking
- Security event logging
- Database query optimization
- WebSocket connection monitoring

## 📖 Documentation

- **CLAUDE.md**: Comprehensive development guide for AI assistants
- **SECURITY.md**: Detailed security requirements and best practices
- **API Documentation**: Interactive docs at `/docs` when server is running

## 🤝 Contributing

This is a production application handling sensitive interview data. All contributions must follow:

1. **Security-first development**: Every feature must implement proper security measures
2. **Modular architecture**: Maintain clean separation of concerns
3. **Comprehensive testing**: Security, unit, and integration tests required
4. **Documentation updates**: Keep all documentation current with changes

## 📝 License

This project contains sensitive interview data handling capabilities. Ensure compliance with data protection regulations in your jurisdiction.

---

**🛡️ Security Notice**: This application handles sensitive interview data. Always follow security best practices and ensure proper data protection compliance.