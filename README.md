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
│   │   ├── api/
│   │   │   └── routes/           # API endpoints (auth, interview, pages, user)
│   │   ├── core/
│   │   │   ├── app.py           # FastAPI application factory
│   │   │   ├── config.py        # Environment configuration
│   │   │   ├── middleware.py    # Security middleware
│   │   │   └── security.py      # Authentication & rate limiting
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic validation models
│   │   └── utils/               # Helper functions
│   ├── static/                  # Frontend assets (modular architecture)
│   │   ├── components/          # Reusable UI components
│   │   │   ├── nav-component.html
│   │   │   ├── nav-component.js
│   │   │   └── nav-component.css
│   │   ├── styles/              # Modular CSS organization
│   │   │   ├── global.css       # Variables, fonts, common layouts
│   │   │   ├── buttons.css      # All button variants
│   │   │   ├── interview.css    # Voice interview interface
│   │   │   ├── database.css     # SQL query interface
│   │   │   ├── dashboard.css    # Dashboard overview
│   │   │   ├── login.css        # Authentication pages
│   │   │   ├── problems.css     # Coding problems interface
│   │   │   └── modal.css        # Modal dialogs
│   │   ├── js/                  # Modular JavaScript
│   │   │   ├── utils.js         # Shared utilities (sanitization, messaging)
│   │   │   ├── interview.js     # Voice interview logic
│   │   │   ├── database.js      # SQL query handling
│   │   │   └── login.js         # Authentication logic
│   │   ├── *.html               # Page templates
│   │   └── assets/              # Images, icons
│   ├── server.py                # FastAPI application entry point
│   ├── pyproject.toml           # Python dependencies & config
│   ├── uv.lock                  # Locked dependency versions
│   ├── .env.example             # Environment template
│   ├── CLAUDE.md                # Development guide
│   └── SECURITY.md              # Security documentation
└── README.md                    # Project documentation
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

## 📊 Database Schema

### **Core Tables**
- **employees**: Employee records with ID, name, department, role
- **interview_sessions**: Session metadata with employee linking and scoring
- **interview_questions**: Question tracking with category and difficulty
- **interview_responses**: Response evaluation with 0.0-1.0 scoring
- **session_reports**: Comprehensive performance analytics

### **Agent Functions**
- `log_question_asked()`: Category/difficulty tracking for analytics
- `log_response_evaluation()`: Real-time response scoring and feedback
- `generate_session_report()`: Comprehensive performance analysis

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

## 🚀 Deployment

### **Environment Configuration**
```bash
# Production environment
DEBUG=false
SESSION_SECRET_KEY=$(openssl rand -hex 32)
ADMIN_PASSWORD=secure-password
DATABASE_URL=sqlite:///interview_sessions.db
```

### **Security Hardening**
```bash
# Database permissions
chmod 600 interview_sessions.db
chown app:app interview_sessions.db

# Server configuration
# HTTPS only, secure headers, rate limiting enabled
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