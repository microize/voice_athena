# CLAUDE.md - Athena Voice Interview Platform

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

**Athena** is a real-time voice-based SQL technical interview application built with modern web technologies. The platform conducts AI-powered SQL interviews using OpenAI's Realtime API with comprehensive session tracking and reporting.

### Core Technologies
- **Backend**: Python 3.12+ with FastAPI framework
- **Real-time Communication**: WebSockets + OpenAI Realtime API
- **Database**: SQLite with aiosqlite for async operations
- **Frontend**: Vanilla JavaScript with modular component architecture
- **Styling**: Modular CSS with CSS variables and PostCSS
- **Package Management**: UV for Python dependencies
- **Security**: Bcrypt, rate limiting, CSP headers, input validation

## Project Structure

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
│   └── SECURITY.md              # Security documentation
└── README.md                    # Project documentation
```

## Development Commands

### Environment Setup
```bash
# Navigate to app directory
cd app/

# Install dependencies
uv sync

# Create environment file
cp .env.example .env
# Add your OpenAI API key to .env

# Start development server
uv run python server.py
```

**Server runs on**: http://localhost:8000

### Testing & Quality
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

## Frontend Architecture - Modular Design

### 🏗️ Component-Based Architecture
The frontend follows a strict modular architecture with clear separation of concerns:

#### **Global Styles** (`styles/global.css`)
- CSS custom properties (variables)
- Font imports via `@import`
- Common layout classes (`.container`, `.main-content`)
- Base typography and reset styles
- Status colors (`--success`, `--error`, `--warning`)

#### **Component Styles**
- **buttons.css**: All button variants (`.button`, `.action-btn`, mic buttons)
- **nav-component.css**: Navigation-specific styles
- **Page-specific CSS**: Only styles unique to that page

#### **JavaScript Modules**
- **utils.js**: Shared utilities (`loadNavigation`, `sanitizeInput`, `showMessage`)
- **Component JS**: Self-contained functionality for specific features
- **Page JS**: Only logic specific to that page

### 🔒 Modular Security Principles

#### **Input Sanitization** (utils.js)
```javascript
function sanitizeInput(input) {
    return input.trim().slice(0, 50).replace(/[<>&"']/g, '');
}
```

#### **Dependency Loading Order**
```html
<!-- Correct loading sequence -->
<script src="/static/components/nav-component.js"></script>
<script src="/static/js/utils.js"></script>
<script src="/static/js/page-specific.js"></script>
```

## Backend Architecture

### 🛡️ Security-First Design

#### **Authentication & Sessions**
- Bcrypt password hashing (12 rounds)
- Secure session management with HTTPOnly cookies
- CSRF protection and rate limiting
- Input validation with Pydantic models

#### **SQL Injection Prevention**
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

#### **Security Headers**
- Content Security Policy (CSP)
- HSTS, X-Frame-Options, X-Content-Type-Options
- XSS Protection and Referrer Policy

### 🎯 Interview System

#### **Real-time Voice Processing**
- WebSocket connections (`/ws/{session_id}`)
- OpenAI Realtime API integration
- 24kHz mono audio format
- Session isolation and cleanup

#### **Database Schema**
- **employees**: Employee records
- **interview_sessions**: Session metadata
- **interview_questions**: Question tracking with categories
- **interview_responses**: Response evaluation (0.0-1.0 scoring)
- **session_reports**: Performance analytics

#### **Agent Functions**
- `log_question_asked()`: Category/difficulty tracking
- `log_response_evaluation()`: Real-time scoring
- `generate_session_report()`: Comprehensive analytics

## Application Endpoints

### **Frontend Routes**
- `/` - Voice interview interface
- `/login` - Authentication
- `/dashboard` - Performance overview
- `/database` - SQL query interface
- `/problems` - Coding challenges

### **API Routes**
- `/api/auth/*` - Authentication endpoints
- `/api/user/*` - User management
- `/api/query` - SQL query execution
- `/ws/{session_id}` - WebSocket connections

## Environment Variables

```bash
# Required
OPENAI_API_KEY=your-openai-api-key
SESSION_SECRET_KEY=your-secret-key

# Optional
DEBUG=false
ADMIN_PASSWORD=secure-password
DATABASE_URL=sqlite:///interview_sessions.db
```

## Security Requirements

### 🚨 Critical Security Standards

#### **Input Validation**
- All user inputs MUST be validated with Pydantic
- Frontend sanitization for XSS prevention
- SQL injection prevention with keyword filtering
- File upload restrictions and validation

#### **Authentication**
- Bcrypt password hashing (minimum 12 rounds)
- Session management with secure cookies
- Rate limiting on authentication endpoints
- CSRF protection on state-changing operations

#### **Data Protection**
- No secrets in version control
- Environment-based configuration
- Secure database file permissions
- Audit logging for sensitive operations

### 🔍 Code Review Checklist

#### **Security**
- [ ] No hardcoded credentials or API keys
- [ ] All inputs validated (frontend AND backend)
- [ ] SQL injection prevention implemented
- [ ] Authentication required for protected routes
- [ ] Rate limiting on sensitive endpoints
- [ ] Security headers configured
- [ ] Error messages don't leak information

#### **Modular Architecture**
- [ ] No duplicate CSS rules across files
- [ ] JavaScript utilities in utils.js
- [ ] CSS variables in global.css
- [ ] Component styles self-contained
- [ ] No inline styles or scripts
- [ ] Proper dependency loading order

## Development Best Practices

### 🏗️ Modular Development
1. **CSS**: Use global.css for shared styles, component-specific files for unique styles
2. **JavaScript**: Shared utilities in utils.js, component logic self-contained
3. **HTML**: Load dependencies in correct order, use semantic markup
4. **Components**: Self-contained with .html, .css, .js files

### 🔒 Security-First Coding
1. **Validate all inputs** - Never trust user data
2. **Use environment variables** - No secrets in code
3. **Implement defense in depth** - Multiple security layers
4. **Log security events** - Audit trails for investigations

### 🧪 Testing Standards
1. **Unit tests** for business logic
2. **Security tests** for authentication and input validation
3. **Integration tests** for API endpoints
4. **End-to-end tests** for critical user flows

## Performance Guidelines

### ⚡ Frontend Optimization
- Modular CSS/JS loading
- Minimal inline styles/scripts
- Efficient component architecture
- Font optimization via global.css

### 🚀 Backend Optimization
- Async/await for all I/O operations
- SQLite with proper indexing
- Connection pooling for database
- Efficient WebSocket management

## Deployment Considerations

### 🔧 Production Setup
```bash
# Environment
DEBUG=false
SESSION_SECRET_KEY=$(openssl rand -hex 32)

# Database security
chmod 600 interview_sessions.db
chown app:app interview_sessions.db

# Server configuration
# HTTPS only, secure headers, rate limiting
```

### 📊 Monitoring
- Application performance monitoring
- Security event logging
- Database query optimization
- WebSocket connection tracking

---

## Important Notes

**🛡️ Security is paramount** - Every feature must follow security-first principles
**📦 Modular architecture** - Maintain clean separation of concerns
**🧪 Test coverage** - Comprehensive testing for all components
**📝 Documentation** - Keep this file updated with architectural changes

**Remember**: This is a production application handling sensitive interview data. Security and code quality are non-negotiable.