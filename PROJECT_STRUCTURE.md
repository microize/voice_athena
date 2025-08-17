# Athena Project Repository Structure

This document provides a comprehensive overview of the Athena Voice Interview Platform repository structure, file organization, and architectural components.

## 📁 Root Directory Structure

```
athena/
├── README.md                     # Main project documentation
├── CLAUDE.md                     # Development guide for AI assistants
├── PROJECT_STRUCTURE.md          # This file - detailed repo structure
└── app/                          # Main application directory
    ├── Core Application Files
    ├── Backend Architecture
    ├── Frontend Assets
    ├── Configuration & Scripts
    ├── Documentation
    ├── Data & Logs
    └── Testing Framework
```

## 🏗️ Application Directory (`app/`)

### **Core Application Files**
```
app/
├── server.py                     # FastAPI application entry point (deprecated)
├── run_athena.py                 # Main application launcher
├── pyproject.toml                # Python dependencies and project config
├── uv.lock                      # Locked dependency versions
├── .env.example                 # Environment variables template
├── CLAUDE.md                    # App-specific development guide
├── README.md                    # App-specific documentation
└── SECURITY.md                  # Security requirements and guidelines
```

### **Backend Architecture (`athena/`)**
```
athena/                          # Core Python package
├── __init__.py                  # Package initialization
├── main.py                      # Application factory and startup
│
├── api/                         # API layer - HTTP endpoints
│   ├── __init__.py
│   └── routes/                  # Modular route definitions
│       ├── __init__.py
│       ├── auth.py              # Authentication endpoints
│       ├── database.py          # Database query endpoints
│       ├── interview.py         # Interview management endpoints
│       ├── pages.py             # Static page routing
│       ├── problems.py          # Coding problems endpoints
│       ├── user.py              # User management endpoints
│       └── websockets.py        # WebSocket endpoints
│
├── core/                        # Core application infrastructure
│   ├── __init__.py
│   ├── app.py                   # FastAPI application factory
│   ├── config.py                # Environment-based configuration
│   ├── database.py              # Database connection and session management
│   ├── dependencies.py          # Dependency injection setup
│   ├── exceptions.py            # Custom exception handlers
│   ├── logging_config.py        # Structured logging configuration
│   ├── middleware.py            # Security and CORS middleware
│   └── security.py              # Authentication and authorization
│
├── services/                    # Business logic layer
│   ├── __init__.py
│   ├── interview_service.py     # Interview session management
│   ├── interview_agent_service.py # AI agent integration
│   ├── user_service.py          # User management business logic
│   ├── problem_service.py       # Coding problems management
│   └── judge0_service.py        # Code execution service integration
│
├── models/                      # Data models and validation
│   ├── __init__.py
│   └── schemas.py               # Pydantic models for request/response validation
│
├── agents/                      # AI agent implementations
│   ├── __init__.py
│   └── [Agent implementations]
│
└── utils/                       # Utility functions and helpers
    ├── __init__.py
    └── [Utility modules]
```

### **Frontend Assets (`static/`)**
```
static/                          # Frontend assets (modular architecture)
├── Page Templates
│   ├── index.html               # Voice interview interface
│   ├── login.html               # Authentication page
│   ├── dashboard.html           # Performance dashboard
│   ├── database.html            # SQL query interface
│   ├── problems.html            # Coding problems list
│   └── problem.html             # Individual problem solver
│
├── components/                  # Reusable UI components
│   ├── nav-component.html       # Navigation bar template
│   ├── nav-component.js         # Navigation functionality
│   └── nav-component.css        # Navigation styling
│
├── styles/                      # Modular CSS architecture
│   ├── global.css               # Variables, fonts, common layouts
│   ├── buttons.css              # All button variants and interactions
│   ├── interview.css            # Voice interview interface styles
│   ├── database.css             # SQL query interface styles
│   ├── dashboard.css            # Dashboard overview styles
│   ├── login.css                # Authentication page styles
│   ├── problems.css             # Coding problems interface styles
│   └── modal.css                # Modal dialog styles
│
├── js/                          # Modular JavaScript
│   ├── utils.js                 # Shared utilities (sanitization, messaging)
│   ├── interview.js             # Voice interview logic and WebSocket handling
│   ├── database.js              # SQL query interface functionality
│   └── login.js                 # Authentication logic
│
├── Assets
│   ├── favicon.ico              # Browser favicon
│   ├── favicon.svg              # Scalable vector favicon
│   ├── athena-logo.png          # Application logo
│   ├── app.js                   # Legacy main application script
│   └── audio-processor-worklet.js # Audio processing for voice interviews
```

### **Configuration & Scripts (`scripts/`)**
```
scripts/                         # Database and utility scripts
├── add_sql_problems.py          # Add SQL problems to database
├── create_favicon.py            # Generate application favicons
├── final_sql_schema_update.py   # Final database schema updates
├── fix_sql_solutions.py         # Fix SQL solution data
├── update_all_sql_schemas.py    # Comprehensive schema updates
└── update_sql_schemas.py        # Standard schema update script
```

### **Documentation (`docs/`)**
```
docs/                            # Additional project documentation
├── ARCHITECTURE.md              # System architecture documentation
├── INTERVIEW_FIXES.md           # Interview system fixes and improvements
└── SETUP_CODING_PLATFORM.md    # Coding platform setup guide
```

### **Data & Logs**
```
data/                            # Application data
└── interview_sessions.db        # SQLite database with interview data

logs/                            # Application logging
├── athena.log                   # General application logs
└── athena_errors.log            # Error-specific logs
```

### **Testing Framework**
```
tests/                           # Test suite
├── __init__.py                  # Test package initialization
├── Unit Tests                   # Individual component tests
├── Integration Tests            # API endpoint tests
├── Security Tests               # Authentication and validation tests
└── End-to-end Tests             # Full user flow tests
```

### **Development Environment**
```
venv/                           # Python virtual environment (if using venv)
server.py.backup               # Backup of legacy server file
```

## 🎯 Key Architectural Patterns

### **Modular Frontend Architecture**
- **Component Isolation**: Each UI component has dedicated .html/.css/.js files
- **Global Styles**: Shared variables and layouts in `global.css`
- **Utility Functions**: Shared JavaScript utilities in `utils.js`
- **Page-Specific Logic**: Individual page scripts with clear dependencies

### **Backend Service Layer**
- **API Routes**: Thin controllers handling HTTP requests
- **Service Layer**: Business logic separated from API layer
- **Core Infrastructure**: Reusable components for database, security, config
- **Models**: Pydantic schemas for type safety and validation

### **Security Integration**
- **Input Validation**: Both frontend sanitization and backend Pydantic validation
- **Authentication**: Secure session management with bcrypt hashing
- **Rate Limiting**: Protection against abuse on sensitive endpoints
- **Security Headers**: CSP, HSTS, and other protective headers

## 📊 Database Schema

### **Core Tables**
```sql
-- Employee management
employees (id, name, department, role, created_at)

-- Session tracking
interview_sessions (id, employee_id, start_time, end_time, overall_score, status)

-- Question management
interview_questions (id, session_id, question_text, category, difficulty, asked_at)

-- Response evaluation
interview_responses (id, question_id, response_text, score, feedback, response_time)

-- Performance analytics
session_reports (id, session_id, strengths, weaknesses, recommendations, created_at)
```

## 🔧 Configuration Files

### **Python Dependencies (`pyproject.toml`)**
```toml
[project]
name = "athena"
version = "1.0.0"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "websockets>=12.0",
    "openai-agents>=1.0.0",
    "aiosqlite>=0.19.0",
    "bcrypt>=4.1.0",
    "pydantic>=2.5.0",
    "python-jose>=3.3.0",
    "slowapi>=0.1.9"
]
```

### **Environment Variables (`.env.example`)**
```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here
SESSION_SECRET_KEY=your-session-secret-key

# Optional
DEBUG=false
ADMIN_PASSWORD=secure-admin-password
DATABASE_URL=sqlite:///data/interview_sessions.db
LOG_LEVEL=INFO
```

## 🚀 Development Workflow

### **Local Development**
```bash
# Setup
cd app/
uv sync
cp .env.example .env
# Edit .env with your keys

# Development
uv run python run_athena.py
# Server runs on http://localhost:8000
```

### **Code Quality**
```bash
# Testing
uv run pytest tests/

# Security scanning
uv run bandit -r athena/

# Code formatting
uv run black athena/
uv run isort athena/

# Type checking
uv run mypy athena/
```

## 📈 File Size Metrics

### **Frontend Optimization Results**
```
CSS Files (styles/):
├── modal.css          85 lines
├── dashboard.css     118 lines
├── buttons.css       182 lines
├── global.css        253 lines
├── problems.css      273 lines
├── login.css         336 lines
├── interview.css     394 lines
└── database.css      444 lines
Total: 2,085 lines

JavaScript Files (js/):
├── utils.js           48 lines
├── interview.js       67 lines
├── login.js          119 lines
└── database.js       226 lines
Total: 460 lines

HTML Files:
├── nav-component.html  21 lines
├── dashboard.html      98 lines
├── database.html      113 lines
├── problems.html      139 lines
├── problem.html       146 lines
├── login.html         151 lines
└── index.html         206 lines
Total: 874 lines
```

## 🛡️ Security Architecture

### **Input Validation Chain**
1. **Frontend Sanitization** (`utils.js`): XSS prevention
2. **Pydantic Validation** (`models/schemas.py`): Type and format validation
3. **SQL Injection Prevention**: Keyword filtering and parameterized queries
4. **Rate Limiting**: Request throttling on sensitive endpoints

### **Authentication Flow**
1. **User Login**: Bcrypt password verification
2. **Session Creation**: Secure cookie with HTTPOnly flags
3. **Request Authorization**: Session validation middleware
4. **CSRF Protection**: State-changing operation protection

## 📝 Documentation Standards

### **File Documentation Requirements**
- **API Routes**: OpenAPI/Swagger documentation
- **Service Methods**: Comprehensive docstrings
- **Security Functions**: Security implications documented
- **Database Schema**: Relationship and constraint documentation

### **Code Review Checklist**
- [ ] Security validation implemented
- [ ] Modular architecture maintained
- [ ] No duplicate code across files
- [ ] Proper error handling
- [ ] Documentation updated
- [ ] Tests written for new features

## 🔄 Continuous Integration

### **Quality Gates**
1. **Security Scanning**: No high-severity vulnerabilities
2. **Test Coverage**: Minimum 80% coverage required
3. **Code Quality**: Black/isort formatting enforced
4. **Type Safety**: MyPy type checking passed
5. **Documentation**: All public APIs documented

### **Deployment Pipeline**
1. **Development**: Local testing with hot reload
2. **Staging**: Integration testing with real services
3. **Production**: Security hardening and performance monitoring

---

This repository structure supports a production-grade voice interview platform with emphasis on security, modularity, and maintainability. Each component is designed for independent development while maintaining clear interfaces and dependencies.