# Athena Repository Development Guide

This guide provides comprehensive information for developers working with the Athena Voice Interview Platform repository, including contribution guidelines, development workflows, and architectural principles.

## 🏛️ Repository Architecture Overview

### **Monorepo Structure**
Athena follows a monorepo architecture with clear separation between application code, documentation, and development tools:

```
athena/
├── 📋 Root Documentation          # Project overview and guides
├── 🏗️ Application Core (app/)     # Main application with modular architecture
├── 🔧 Development Tools           # Scripts, configs, and utilities
├── 📊 Data Management             # Database and logging infrastructure
└── 🧪 Testing Framework           # Comprehensive test suite
```

## 📂 Detailed Directory Structure

### **Root Level Files**
```
/
├── README.md                     # 📖 Main project documentation
├── CLAUDE.md                     # 🤖 AI assistant development guide
├── PROJECT_STRUCTURE.md          # 🏗️ Repository structure documentation
└── REPOSITORY_GUIDE.md           # 📋 This file - development guide
```

### **Application Directory (`app/`)**

#### **Core Application Infrastructure**
```
app/
├── 🚀 Entry Points
│   ├── run_athena.py             # Main application launcher
│   ├── server.py.backup         # Legacy server backup
│   └── main.py → athena/main.py  # Application factory
│
├── ⚙️ Configuration
│   ├── pyproject.toml            # Python dependencies and metadata
│   ├── uv.lock                  # Locked dependency versions
│   └── .env.example             # Environment template
│
└── 📖 Documentation
    ├── CLAUDE.md                 # App-specific AI guide
    ├── README.md                 # App-specific documentation
    └── SECURITY.md               # Security requirements
```

#### **Backend Package (`athena/`)**
```
athena/                          # 🐍 Core Python package
├── 📦 Package Definition
│   ├── __init__.py              # Package initialization
│   └── main.py                  # FastAPI application factory
│
├── 🌐 API Layer (Thin Controllers)
│   └── api/
│       ├── __init__.py
│       └── routes/              # RESTful API endpoints
│           ├── auth.py          # 🔐 Authentication & authorization
│           ├── database.py      # 📊 Database query interface
│           ├── interview.py     # 🎤 Interview session management
│           ├── pages.py         # 📄 Static page routing
│           ├── problems.py      # 💻 Coding problems API
│           ├── user.py          # 👤 User management
│           └── websockets.py    # 🔌 Real-time communication
│
├── 🏗️ Core Infrastructure
│   └── core/
│       ├── app.py               # FastAPI app factory & middleware setup
│       ├── config.py            # Environment-based configuration
│       ├── database.py          # Database connection & session management
│       ├── dependencies.py      # Dependency injection container
│       ├── exceptions.py        # Custom exception handlers
│       ├── logging_config.py    # Structured logging setup
│       ├── middleware.py        # Security, CORS, and request middleware
│       └── security.py          # Authentication, hashing, JWT handling
│
├── 💼 Business Logic Layer
│   └── services/
│       ├── interview_service.py      # Interview session business logic
│       ├── interview_agent_service.py # AI agent integration
│       ├── user_service.py          # User management business logic
│       ├── problem_service.py       # Coding problems management
│       └── judge0_service.py        # External code execution service
│
├── 📋 Data Models & Validation
│   └── models/
│       └── schemas.py           # Pydantic models for API validation
│
├── 🤖 AI Agent Integration
│   └── agents/
│       └── [Agent implementations for interview conduct]
│
└── 🔧 Utilities & Helpers
    └── utils/
        └── [Shared utility functions]
```

#### **Frontend Assets (`static/`)**
```
static/                          # 🎨 Frontend (Modular Component Architecture)
├── 📄 Application Pages
│   ├── index.html               # 🎤 Voice interview interface
│   ├── login.html               # 🔐 Authentication page
│   ├── dashboard.html           # 📊 Performance dashboard
│   ├── database.html            # 🗃️ SQL query interface
│   ├── problems.html            # 💻 Coding problems list
│   └── problem.html             # 📝 Individual problem solver
│
├── 🧩 Reusable Components (Component-Based Architecture)
│   └── components/
│       ├── nav-component.html   # Navigation bar template
│       ├── nav-component.js     # Navigation functionality & state
│       └── nav-component.css    # Navigation styling
│
├── 🎨 Modular Styling (CSS Architecture)
│   └── styles/
│       ├── global.css           # 🌐 Variables, fonts, layouts, utilities
│       ├── buttons.css          # 🔘 All button variants & interactions
│       ├── interview.css        # 🎤 Voice interview interface styles
│       ├── database.css         # 🗃️ SQL query interface styles
│       ├── dashboard.css        # 📊 Dashboard overview styles
│       ├── login.css            # 🔐 Authentication page styles
│       ├── problems.css         # 💻 Coding problems styles
│       └── modal.css            # 📦 Modal dialog styles
│
├── ⚡ JavaScript Modules (Modular JS Architecture)
│   └── js/
│       ├── utils.js             # 🔧 Shared utilities (sanitization, messaging)
│       ├── interview.js         # 🎤 Voice interview & WebSocket logic
│       ├── database.js          # 🗃️ SQL query interface functionality
│       └── login.js             # 🔐 Authentication logic
│
└── 📁 Static Assets
    ├── favicon.ico              # Browser favicon
    ├── favicon.svg              # Scalable vector favicon  
    ├── athena-logo.png          # Application branding
    ├── app.js                   # Legacy application script
    └── audio-processor-worklet.js # Audio processing worklet
```

#### **Development Infrastructure**
```
├── 📜 Automation Scripts
│   └── scripts/
│       ├── add_sql_problems.py      # Database population scripts
│       ├── create_favicon.py        # Asset generation
│       ├── final_sql_schema_update.py # Schema management
│       ├── fix_sql_solutions.py     # Data correction scripts
│       ├── update_all_sql_schemas.py # Bulk schema updates
│       └── update_sql_schemas.py    # Standard schema updates
│
├── 📚 Extended Documentation
│   └── docs/
│       ├── ARCHITECTURE.md          # System architecture deep-dive
│       ├── INTERVIEW_FIXES.md       # Interview system improvements
│       └── SETUP_CODING_PLATFORM.md # Platform setup guide
│
├── 💾 Application Data
│   └── data/
│       └── interview_sessions.db    # SQLite database
│
├── 📝 Application Logs
│   └── logs/
│       ├── athena.log              # General application logs
│       └── athena_errors.log       # Error-specific logs
│
├── 🧪 Testing Framework
│   └── tests/
│       ├── __init__.py             # Test package setup
│       ├── test_*.py               # Unit tests
│       ├── integration/            # Integration tests
│       ├── security/               # Security tests
│       └── e2e/                    # End-to-end tests
│
└── 🐍 Development Environment
    └── venv/                       # Python virtual environment (optional)
```

## 🔄 Development Workflow

### **Getting Started**
```bash
# 1. Clone and Setup
git clone <repository-url>
cd athena/app/

# 2. Environment Setup
uv sync                          # Install dependencies
cp .env.example .env            # Create environment file
# Edit .env with your API keys

# 3. Development Server
uv run python run_athena.py     # Start development server
# Access: http://localhost:8000
```

### **Development Commands**
```bash
# 🏃 Run Application
uv run python run_athena.py     # Development server with hot reload

# 🧪 Testing
uv run pytest                   # Run all tests
uv run pytest tests/unit/       # Unit tests only
uv run pytest tests/security/   # Security tests
uv run pytest --cov=athena     # Coverage report

# 🔍 Code Quality
uv run black athena/            # Code formatting
uv run isort athena/            # Import sorting
uv run mypy athena/             # Type checking
uv run bandit -r athena/        # Security scanning

# 📊 Database Management
python scripts/update_sql_schemas.py    # Update database schema
python scripts/add_sql_problems.py      # Add coding problems
```

## 🏗️ Architectural Principles

### **1. Modular Frontend Architecture**
```
Principle: Component Isolation with Shared Utilities

Structure:
├── Global Layer (global.css, utils.js)     # Shared resources
├── Component Layer (components/)           # Reusable components  
├── Page Layer (*.html, page-specific.css) # Page implementations
└── Asset Layer (images, fonts, icons)     # Static resources

Benefits:
✅ No code duplication
✅ Clear dependency hierarchy
✅ Easy maintenance and updates
✅ Consistent styling and behavior
```

### **2. Backend Service Layer Pattern**
```
Layer Architecture:

API Layer (routes/)              # HTTP request handling
    ↓ delegates to
Service Layer (services/)        # Business logic
    ↓ uses
Core Layer (core/)              # Infrastructure (DB, auth, config)
    ↓ validates with  
Model Layer (models/)           # Data validation and schemas

Benefits:
✅ Clear separation of concerns
✅ Testable business logic
✅ Reusable infrastructure components
✅ Type-safe data handling
```

### **3. Security-First Design**
```
Security Integration Points:

Frontend: Input sanitization, XSS prevention
    ↓
API Layer: Request validation, rate limiting
    ↓  
Service Layer: Business rule enforcement
    ↓
Database Layer: SQL injection prevention, access control

Security Features:
🔐 Multi-layer input validation
🔐 Bcrypt password hashing
🔐 Session management with secure cookies
🔐 Rate limiting and CSRF protection
🔐 Comprehensive security headers
```

## 🧩 Component Development Guidelines

### **Frontend Component Structure**
```html
<!-- components/new-component.html -->
<div class="new-component">
    <!-- Component template -->
</div>
```

```css
/* components/new-component.css */
.new-component {
    /* Component-specific styles */
    /* Use CSS variables from global.css */
    color: var(--foreground);
    background: var(--screen);
}
```

```javascript
// components/new-component.js
class NewComponent {
    constructor() {
        this.init();
    }
    
    init() {
        // Component initialization
    }
    
    load(config = {}) {
        // Component loading logic
    }
}

// Export for global use
window.NewComponent = new NewComponent();
```

### **Backend Service Development**
```python
# services/new_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.schemas import RequestModel, ResponseModel
from ..core.exceptions import BusinessLogicError

class NewService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def process_request(self, request: RequestModel) -> ResponseModel:
        """
        Process business logic with proper error handling
        """
        try:
            # Business logic implementation
            result = await self._perform_operation(request)
            return ResponseModel(data=result)
        except Exception as e:
            raise BusinessLogicError(f"Operation failed: {e}")
    
    async def _perform_operation(self, request: RequestModel):
        # Private implementation
        pass
```

### **API Route Development**
```python
# api/routes/new_endpoint.py
from fastapi import APIRouter, Depends, HTTPException
from ..services.new_service import NewService
from ..models.schemas import RequestModel, ResponseModel
from ..core.dependencies import get_new_service

router = APIRouter(prefix="/api/new", tags=["new"])

@router.post("/process", response_model=ResponseModel)
async def process_endpoint(
    request: RequestModel,
    service: NewService = Depends(get_new_service)
):
    """
    Process request with proper validation and error handling
    """
    try:
        result = await service.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🔒 Security Development Standards

### **Input Validation Chain**
```python
# 1. Frontend Sanitization (utils.js)
function sanitizeInput(input) {
    return input.trim().slice(0, 50).replace(/[<>&"']/g, '');
}

# 2. Pydantic Validation (models/schemas.py)
class UserInput(BaseModel):
    data: str = Field(..., min_length=1, max_length=5000)
    
    @validator('data')
    def validate_input(cls, v):
        # Custom validation logic
        return v

# 3. Service Layer Validation (services/)
async def process_input(self, input_data: str):
    # Additional business rule validation
    if not self._is_valid_input(input_data):
        raise ValidationError("Invalid input")
```

### **Authentication Flow**
```python
# 1. Login Endpoint (api/routes/auth.py)
@router.post("/login")
async def login(credentials: LoginRequest):
    user = await auth_service.authenticate(credentials)
    session = await auth_service.create_session(user)
    return {"access_token": session.token}

# 2. Protected Endpoint
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"user": current_user}

# 3. Middleware Security (core/middleware.py)
async def security_middleware(request: Request, call_next):
    # Rate limiting, CSRF protection, etc.
    response = await call_next(request)
    # Security headers
    return response
```

## 📊 Database Development

### **Schema Management**
```python
# Database Schema Evolution
scripts/
├── update_sql_schemas.py        # Standard schema updates
├── final_sql_schema_update.py   # Major version updates
└── add_sql_problems.py          # Data population

# Schema Update Process:
1. Create update script in scripts/
2. Test on development database
3. Document changes in docs/
4. Apply to production with backup
```

### **Database Service Pattern**
```python
# core/database.py
class DatabaseService:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL)
        self.SessionLocal = async_sessionmaker(self.engine)
    
    async def get_session(self) -> AsyncSession:
        async with self.SessionLocal() as session:
            yield session

# services/base_service.py
class BaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, obj_in: BaseModel):
        # Generic create operation
        pass
    
    async def get(self, id: int):
        # Generic get operation
        pass
```

## 🧪 Testing Standards

### **Test Structure**
```
tests/
├── unit/                       # Unit tests (individual functions)
│   ├── test_services.py        # Business logic tests
│   ├── test_models.py          # Data validation tests
│   └── test_utils.py           # Utility function tests
├── integration/                # Integration tests (API endpoints)
│   ├── test_auth_api.py        # Authentication flow tests
│   ├── test_interview_api.py   # Interview system tests
│   └── test_database_api.py    # Database query tests
├── security/                   # Security-specific tests
│   ├── test_authentication.py  # Auth security tests
│   ├── test_input_validation.py # Input sanitization tests
│   └── test_rate_limiting.py   # Rate limiting tests
└── e2e/                       # End-to-end tests
    ├── test_interview_flow.py  # Complete interview process
    └── test_user_journey.py    # Full user experience
```

### **Test Examples**
```python
# tests/security/test_input_validation.py
import pytest
from athena.api.routes.database import router

class TestInputValidation:
    async def test_sql_injection_prevention(self, client):
        malicious_query = "'; DROP TABLE users; --"
        response = await client.post(
            "/api/database/query", 
            json={"query": malicious_query}
        )
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]
    
    async def test_xss_prevention(self, client):
        xss_payload = "<script>alert('xss')</script>"
        response = await client.post(
            "/api/user/profile",
            json={"name": xss_payload}
        )
        # Should be sanitized or rejected
        assert "<script>" not in response.json()["name"]
```

## 📝 Documentation Standards

### **Code Documentation**
```python
# Service Layer Documentation
class InterviewService:
    """
    Manages interview sessions and AI agent interactions.
    
    This service handles the complete interview lifecycle including:
    - Session creation and management
    - AI agent coordination
    - Response evaluation and scoring
    - Performance report generation
    
    Security Considerations:
    - All user inputs are validated through Pydantic models
    - Session isolation prevents data leakage between interviews
    - Audio data is processed in memory and not stored
    """
    
    async def create_session(self, employee_id: str) -> InterviewSession:
        """
        Create a new interview session for an employee.
        
        Args:
            employee_id: Validated employee identifier
            
        Returns:
            InterviewSession: New session with unique ID and metadata
            
        Raises:
            ValidationError: If employee_id is invalid
            DatabaseError: If session creation fails
            
        Security:
            - Employee ID is validated against database
            - Session ID is cryptographically secure UUID
        """
```

### **API Documentation**
```python
# API Endpoint Documentation
@router.post(
    "/interview/start",
    response_model=InterviewSessionResponse,
    summary="Start new interview session",
    description="""
    Create and start a new voice-based SQL interview session.
    
    **Process:**
    1. Validates employee credentials
    2. Creates secure session with unique ID
    3. Initializes AI agent for interview conduct
    4. Returns WebSocket connection details
    
    **Security:**
    - Rate limited to 3 sessions per hour per employee
    - Session tokens expire after 2 hours of inactivity
    - All audio processing happens in memory
    """,
    responses={
        201: {"description": "Session created successfully"},
        400: {"description": "Invalid employee credentials"},
        429: {"description": "Rate limit exceeded"},
    }
)
async def start_interview(request: StartInterviewRequest):
    """Start new interview session endpoint"""
```

## 🚀 Deployment Guide

### **Environment Configuration**
```bash
# Production Environment Variables
DEBUG=false
SESSION_SECRET_KEY=$(openssl rand -hex 32)
ADMIN_PASSWORD=$(openssl rand -base64 32)
DATABASE_URL=sqlite:///data/interview_sessions.db
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
SESSION_TIMEOUT_MINUTES=120
```

### **Production Security Checklist**
```bash
# Database Security
chmod 600 data/interview_sessions.db
chown app:app data/interview_sessions.db

# File Permissions
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;

# SSL/TLS Configuration
# - Force HTTPS redirects
# - Set secure cookie flags
# - Configure CSP headers

# Monitoring Setup
# - Application performance monitoring
# - Security event logging
# - Database query monitoring
# - WebSocket connection tracking
```

## 🔄 Contribution Workflow

### **Development Process**
1. **Feature Branch**: Create from `main` with descriptive name
2. **Development**: Follow architectural patterns and security standards
3. **Testing**: Write comprehensive tests (unit, integration, security)
4. **Documentation**: Update relevant documentation files
5. **Code Review**: Security and architecture review required
6. **Deployment**: Staging testing before production

### **Code Review Standards**
```markdown
## Code Review Checklist

### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention implemented
- [ ] Authentication required for protected endpoints
- [ ] Rate limiting on sensitive operations
- [ ] Security headers properly configured

### Architecture
- [ ] Modular design principles followed
- [ ] No code duplication across components
- [ ] Proper separation of concerns
- [ ] Type hints used throughout
- [ ] Error handling comprehensive

### Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for APIs
- [ ] Security tests for auth flows
- [ ] Test coverage above 80%

### Documentation
- [ ] Code properly documented
- [ ] API changes reflected in docs
- [ ] Security implications noted
- [ ] Breaking changes highlighted
```

---

This repository guide ensures consistent development practices while maintaining the security and modular architecture that makes Athena a production-ready voice interview platform.