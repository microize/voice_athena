# CLAUDE.md - Athena Voice Interview Platform

This file provides comprehensive guidance to Claude Code (claude.ai/code) when working with this repository. It contains detailed explanations of every file, architectural patterns, and development workflows.

## Project Overview

**Athena** is a comprehensive voice-based SQL technical interview platform with advanced AI integration and modular architecture. The system combines real-time voice processing, intelligent question generation, automated scoring, and comprehensive analytics to deliver professional-grade technical interviews.

### **Core Components**
1. **Voice Interview Engine** (`app/athena/`): FastAPI server with OpenAI Realtime API integration
2. **Database Analytics Platform**: Web-based SQL query interface with security controls
3. **Coding Assessment System**: Supplementary programming challenges with Judge0 integration
4. **User Management System**: Authentication, progress tracking, and performance analytics
5. **Modular Frontend Architecture**: Component-based design with strict separation of concerns

### **Technology Integration**
- **OpenAI Realtime API**: Real-time voice communication and intelligent response evaluation
- **FastAPI Framework**: Modern async Python web framework with automatic API documentation
- **SQLite + aiosqlite**: Lightweight, async database for session tracking and analytics
- **WebSocket Communication**: Real-time bidirectional communication for voice interviews
- **Judge0 API**: Remote code execution for programming challenges
- **Modular CSS/JS**: Component-based frontend with clear architectural boundaries

## Development Commands

### **Primary Application** (`app/` directory)
```bash
# Navigate to application directory
cd app/

# Install dependencies with UV
uv sync

# Alternative dependency installation
pip install fastapi uvicorn websockets openai-agents aiosqlite

# Start development server
uv run python athena/main.py

# Alternative entry points
python athena/main.py
uv run python run_athena.py
```

**Development Server**: http://localhost:8003 (configurable via HOST/PORT env vars)

### **Testing and Quality Assurance**
```bash
# Run test suite
uv run pytest

# Security scanning
uv run bandit -r athena/

# Code formatting
uv run black athena/
uv run isort athena/

# Type checking
uv run mypy athena/

# Linting
uv run flake8 athena/
```

## Detailed File Architecture

### **🏗️ Core Application Framework** (`app/athena/core/`)

#### **`app.py`** - FastAPI Application Factory
- **Purpose**: Creates and configures the main FastAPI application instance
- **Key Functions**:
  - `create_app()`: Application factory with middleware setup
  - `lifespan()`: Async context manager for startup/shutdown events
- **Architecture**: Implements dependency injection and middleware orchestration
- **Dependencies**: Integrates security headers, CORS, request logging, error handling
- **Startup Process**: Database initialization, configuration validation, service registration

#### **`config.py`** - Environment Configuration Management
- **Purpose**: Centralized configuration with environment variable loading
- **Key Classes**:
  - `Settings`: Main configuration class with validation
- **Configuration Domains**:
  - API keys (OpenAI, Judge0)
  - Database connection settings
  - Security parameters (session keys, rate limits)
  - Server configuration (host, port, debug mode)
  - Supported programming languages for Judge0
- **Validation**: Runtime configuration validation with warnings for missing keys

#### **`database.py`** - Database Connection and Schema Management
- **Purpose**: SQLite database initialization and connection handling
- **Key Functions**:
  - `init_database()`: Creates tables and indexes
  - `get_db_connection()`: Async connection factory
- **Schema Management**: 
  - Employee tracking and session management
  - Interview questions and response evaluation
  - Performance analytics and reporting
  - Coding problem submissions
- **Async Operations**: Full aiosqlite integration for non-blocking database access

#### **`security.py`** - Authentication and Security Controls
- **Purpose**: User authentication, password hashing, rate limiting
- **Key Functions**:
  - `hash_password()`: Bcrypt password hashing (12 rounds)
  - `verify_password()`: Secure password verification
  - `require_auth()`: Authentication dependency for protected routes
  - `rate_limit()`: Request rate limiting middleware
- **Security Features**:
  - Session-based authentication with secure cookies
  - Configurable rate limiting (requests per time window)
  - Login attempt tracking and lockout
  - CSRF protection for state-changing operations

#### **`middleware.py`** - HTTP Middleware Stack
- **Purpose**: Request/response processing pipeline
- **Middleware Components**:
  - `SecurityHeadersMiddleware`: CSP, HSTS, X-Frame-Options, etc.
  - `RequestLoggingMiddleware`: Structured request/response logging
  - `ErrorHandlingMiddleware`: Global exception handling and sanitization
- **Security Headers**: Comprehensive security header implementation
- **Logging**: Structured logging with request IDs and timing information

#### **`dependencies.py`** - Dependency Injection Providers
- **Purpose**: FastAPI dependency injection for services and database connections
- **Key Functions**:
  - `get_interview_service()`: Interview service provider
  - `get_user_service()`: User management service provider
  - `get_problem_service()`: Coding problem service provider
  - `get_judge0_service()`: Code execution service provider
- **Pattern**: Implements dependency injection pattern for service layer isolation

#### **`exceptions.py`** - Custom Exception Classes
- **Purpose**: Application-specific exception hierarchy
- **Exception Types**:
  - Authentication and authorization errors
  - Database connection and query errors
  - External API integration errors
  - Validation and input sanitization errors
- **Error Handling**: Structured error responses with proper HTTP status codes

#### **`logging_config.py`** - Structured Logging Configuration
- **Purpose**: Centralized logging setup with multiple handlers
- **Features**:
  - File-based logging with rotation
  - Structured JSON logging for production
  - Separate error log streams
  - Configurable log levels per module
- **Handlers**: Console, file, and error-specific log handlers

### **🔌 API Layer** (`app/athena/api/routes/`)

#### **`auth.py`** - Authentication Endpoints
- **Purpose**: User login, logout, and session management
- **Endpoints**:
  - `POST /api/auth/login`: User authentication with rate limiting
  - `POST /api/auth/logout`: Session termination and cleanup
  - `POST /api/auth/register`: New user registration (if enabled)
  - `GET /api/auth/verify`: Session validation and refresh
- **Security**: Rate limiting, input validation, secure session cookies
- **Error Handling**: Proper error responses without information leakage

#### **`interview.py`** - Interview Session Management
- **Purpose**: Interview session lifecycle and progress tracking
- **Endpoints**:
  - `POST /api/start-interview`: Initialize new interview session
  - `GET /api/user/progress`: Retrieve user performance analytics
- **Integration**: Works with WebSocket handlers for real-time communication
- **Session Management**: Employee ID validation and session tracking

#### **`database.py`** - SQL Query Execution API
- **Purpose**: Secure SQL query interface for database analytics
- **Endpoints**:
  - `POST /api/query`: Execute validated SQL SELECT queries
  - `GET /api/database/schema`: Database schema information
- **Security**: SQL injection prevention, read-only query validation
- **Validation**: Pydantic models for query validation and sanitization

#### **`problems.py`** - Coding Problem Management
- **Purpose**: CRUD operations for programming challenges
- **Endpoints**:
  - `GET /api/problems`: List problems with filtering and pagination
  - `GET /api/problems/{id}`: Individual problem details
  - `POST /api/problems/{id}/submit`: Code submission and evaluation
  - `GET /api/problems/{id}/submissions`: Submission history
- **Integration**: Judge0 API for code execution and testing

#### **`user.py`** - User Profile and Analytics
- **Purpose**: User management and progress tracking
- **Endpoints**:
  - `GET /api/user/profile`: User profile information
  - `PUT /api/user/profile`: Profile updates
  - `GET /api/user/statistics`: Performance analytics
- **Analytics**: Interview performance, problem-solving statistics, progress tracking

#### **`websockets.py`** - WebSocket Connection Management
- **Purpose**: Real-time communication for voice interviews
- **WebSocket Endpoints**:
  - `/ws/{session_id}`: Voice interview communication channel
- **Features**:
  - Session isolation and management
  - Audio stream handling
  - Real-time agent communication
  - Connection lifecycle management

#### **`pages.py`** - HTML Page Serving
- **Purpose**: Serve frontend HTML templates
- **Routes**:
  - `GET /`: Voice interview interface
  - `GET /login`: Authentication page
  - `GET /dashboard`: User dashboard
  - `GET /database`: SQL query interface
  - `GET /problems`: Problem list view
  - `GET /problems/{id}`: Individual problem view
- **Template Serving**: Static HTML with dynamic content injection

### **🔧 Service Layer** (`app/athena/services/`)

#### **`interview_agent_service.py`** - OpenAI Realtime API Integration
- **Purpose**: Real-time voice interview coordination with AI agents
- **Key Functions**:
  - `log_question_asked()`: Track interview questions by category/difficulty
  - `log_response_evaluation()`: Real-time response scoring (0.0-1.0)
  - `generate_session_report()`: Comprehensive performance analysis
- **Agent Integration**: OpenAI Realtime API with function tools
- **Session Management**: Global session tracking for database operations
- **Question Categories**: joins, subqueries, window_functions, cte, performance, indexing

#### **`interview_service.py`** - Interview Session Orchestration
- **Purpose**: High-level interview session management and coordination
- **Key Functions**:
  - `create_interview_session()`: Initialize new session with employee tracking
  - `get_session_details()`: Retrieve session information and progress
  - `update_session_status()`: Session state management
  - `generate_analytics()`: Performance metrics and reporting
- **Employee Integration**: Links sessions to employee records for analytics
- **Session Lifecycle**: Complete session management from creation to cleanup

#### **`user_service.py`** - User Management and Analytics
- **Purpose**: User account management and progress tracking
- **Key Functions**:
  - `create_user()`: User account creation with validation
  - `authenticate_user()`: Secure user authentication
  - `get_user_progress()`: Comprehensive progress analytics
  - `update_user_profile()`: Profile management
- **Analytics**: Interview performance, problem-solving statistics, skill progression
- **Security**: Password hashing, session management, access control

#### **`problem_service.py`** - Coding Problem Management
- **Purpose**: Programming challenge lifecycle management
- **Key Functions**:
  - `get_problems()`: Problem listing with filtering and difficulty sorting
  - `get_problem_details()`: Individual problem data with test cases
  - `submit_solution()`: Code submission processing
  - `evaluate_submission()`: Integration with Judge0 for code execution
- **Problem Categories**: SQL, algorithms, data structures, system design
- **Difficulty Levels**: Beginner, intermediate, advanced with skill progression

#### **`judge0_service.py`** - Code Execution Service
- **Purpose**: Remote code execution via Judge0 API
- **Key Functions**:
  - `execute_code()`: Submit code for execution with language detection
  - `get_submission_result()`: Retrieve execution results and timing
  - `validate_test_cases()`: Test case validation and scoring
- **Language Support**: Python, JavaScript, Java, C++, C#, Go, Rust, PHP, Ruby
- **Security**: Sandboxed execution environment with resource limits
- **Integration**: Async API calls with proper error handling and timeouts

### **📊 Data Models** (`app/athena/models/`)

#### **`schemas.py`** - Pydantic Validation Models
- **Purpose**: Data validation, serialization, and API schema definition
- **Key Models**:
  - `UserLogin`: Login request validation with sanitization
  - `InterviewSession`: Session data with employee linking
  - `QueryRequest`: SQL query validation with security checks
  - `ProblemSubmission`: Code submission with language validation
  - `UserProgress`: Analytics data for progress tracking
- **Validation**: Input sanitization, type checking, business rule enforcement
- **Security**: SQL injection prevention, XSS protection, input length limits

### **🎯 Frontend Architecture** (`app/static/`)

#### **JavaScript Modules** (`static/js/`)

##### **`utils.js`** - Shared Utility Functions
- **Purpose**: Common utilities used across all frontend components
- **Key Functions**:
  - `loadNavigation()`: Dynamic navigation component loading
  - `sanitizeInput()`: Client-side input sanitization for XSS prevention
  - `showMessage()`: Unified message display system
  - `apiCall()`: Standardized API request wrapper with error handling
- **Security**: Input sanitization, XSS prevention, CSRF token handling
- **Modularity**: Shared functions to avoid code duplication

##### **`interview.js`** - Voice Interview Logic
- **Purpose**: WebSocket communication and audio processing for voice interviews
- **Key Features**:
  - WebSocket connection management with reconnection logic
  - Audio capture and streaming (24kHz mono format)
  - Real-time transcription display
  - Session state management (connecting, active, ended)
- **WebSocket Events**: Connection, audio data, transcription, session updates
- **Audio Processing**: WebAudio API integration with worklet processing

##### **`database.js`** - SQL Query Interface
- **Purpose**: Interactive SQL query execution and result display
- **Features**:
  - Query editor with syntax highlighting
  - Result table formatting and pagination
  - Query history and favorites
  - Error display and query validation
- **Security**: Client-side query validation before submission
- **UX**: Auto-completion, query templates, result export options

##### **`login.js`** - Authentication Form Handling
- **Purpose**: User authentication interface logic
- **Features**:
  - Form validation and submission
  - Password strength indication
  - Rate limiting feedback
  - Remember me functionality
- **Security**: Client-side validation, secure form submission
- **UX**: Progressive enhancement, accessibility compliance

##### **`problem.js`** - Individual Problem View
- **Purpose**: Single problem interface with code editor
- **Features**:
  - Code editor with syntax highlighting
  - Language selection and validation
  - Test case display and execution
  - Submission history and results
- **Editor**: Monaco Editor integration with language support
- **Testing**: Real-time code execution and feedback

##### **`problems.js`** - Problem List and Filtering
- **Purpose**: Problem discovery and filtering interface
- **Features**:
  - Dynamic filtering by difficulty, category, status
  - Pagination and infinite scroll
  - Progress indicators and statistics
  - Search functionality
- **Performance**: Lazy loading, virtualization for large lists
- **Analytics**: Progress tracking, completion statistics

#### **CSS Architecture** (`static/styles/`)

##### **`global.css`** - Foundation Styles
- **Purpose**: CSS custom properties, base styles, and layout foundations
- **Contents**:
  - CSS custom properties for colors, spacing, typography
  - Font imports and font-face declarations
  - Base element styling and CSS reset
  - Common layout classes (`.container`, `.main-content`)
  - Utility classes for spacing, display, positioning
- **Design System**: Consistent design tokens across all components

##### **Component-Specific Styles**
- **`buttons.css`**: All button variants, states, and interactions
- **`interview.css`**: Voice interview interface with microphone controls
- **`database.css`**: SQL query interface and result table styling
- **`dashboard.css`**: User dashboard layout and widgets
- **`login.css`**: Authentication form styling with error states
- **`problems.css`**: Problem list and individual problem view styling
- **`modal.css`**: Modal dialog system with overlay and transitions

#### **Advanced CSS System** (`static/styles-new/`)
- **ITCSS Architecture**: Inverted Triangle CSS methodology
- **01-settings/**: CSS custom properties and design tokens
- **02-tools/**: Utility classes and mixins
- **03-generic/**: CSS reset and normalization
- **04-elements/**: Base element styling
- **05-objects/**: Layout and structural patterns
- **06-components/**: UI component library
- **07-pages/**: Page-specific overrides and layouts

#### **HTML Templates** (`static/*.html`)

##### **`index.html`** - Voice Interview Interface
- **Purpose**: Main interview application with audio controls
- **Features**:
  - Employee ID input and validation
  - WebSocket connection controls
  - Real-time audio visualization
  - Interview status and progress display
- **Integration**: WebSocket, WebAudio API, OpenAI Realtime API

##### **`login.html`** - Authentication Interface
- **Purpose**: User login and session management
- **Features**:
  - Secure authentication form
  - Rate limiting feedback
  - Password recovery options
  - Registration link (if enabled)
- **Security**: CSRF protection, input validation, secure submission

##### **`dashboard.html`** - User Dashboard
- **Purpose**: Performance overview and navigation hub
- **Features**:
  - Performance metrics and analytics
  - Recent activity timeline
  - Quick action buttons
  - Progress visualization
- **Analytics**: Charts, graphs, achievement system

##### **`database.html`** - SQL Query Interface
- **Purpose**: Interactive database exploration and analytics
- **Features**:
  - Query editor with syntax highlighting
  - Result table with sorting and filtering
  - Schema browser and table exploration
  - Query history and saved queries
- **Security**: Read-only access, query validation

##### **`problems.html`** - Problem List View
- **Purpose**: Coding challenge discovery and navigation
- **Features**:
  - Problem filtering and search
  - Difficulty and category organization
  - Progress tracking and completion status
  - Performance analytics
- **UX**: Responsive grid, infinite scroll, advanced filtering

##### **`problem.html`** - Individual Problem View
- **Purpose**: Single problem interface with code editor
- **Features**:
  - Problem description and examples
  - Multi-language code editor
  - Test case execution and validation
  - Submission history and analytics
- **Editor**: Full IDE experience with debugging support

### **🗄️ Database and Scripts**

#### **Database** (`app/data/`)
- **`interview_sessions.db`**: SQLite database with complete schema
  - Employee tracking and session management
  - Interview questions and response evaluation
  - Performance analytics and reporting
  - Coding problem submissions and results

#### **Maintenance Scripts** (`app/scripts/`)

##### **`add_sql_problems.py`** - Database Seeding
- **Purpose**: Populate database with SQL practice problems
- **Features**: Netflix, Amazon, Google-style SQL interview questions
- **Categories**: Window functions, joins, CTEs, performance optimization

##### **`create_favicon.py`** - Asset Generation
- **Purpose**: Generate application favicon from source images
- **Output**: Multiple favicon formats for browser compatibility

##### **Schema Management Scripts**
- **`update_sql_schemas.py`**: Individual table schema updates
- **`update_all_sql_schemas.py`**: Batch schema migration
- **`final_sql_schema_update.py`**: Production schema deployment
- **`fix_sql_solutions.py`**: Repair corrupted problem solutions

### **📄 Configuration Files**

#### **`pyproject.toml`** - Project Configuration
- **Purpose**: Python project metadata and dependency management
- **Dependencies**: Core and development dependencies with version constraints
- **Scripts**: Entry point definitions for application execution
- **Tool Configuration**: Black, isort, pytest, mypy configuration

#### **`uv.lock`** - Dependency Lock File
- **Purpose**: Reproducible dependency resolution
- **Generated**: Automatically created by UV package manager
- **Contains**: Exact versions and checksums for all dependencies

## Environment Configuration

### **Environment Variables** (`.env` file)
```bash
# Required API Keys
OPENAI_API_KEY=your-openai-api-key-here
JUDGE0_API_KEY=your-judge0-api-key-here

# Database Configuration
DB_PATH=data/interview_sessions.db

# Server Configuration  
HOST=0.0.0.0
PORT=8003
DEBUG=false

# Security Configuration
SESSION_SECRET_KEY=your-secure-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_WINDOW=900

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Logging
LOG_LEVEL=INFO

# Optional: Default User Credentials (Development Only)
ADMIN_PASSWORD=secure-admin-password
DEMO_PASSWORD=secure-demo-password
```

## Security Architecture

### **Input Validation Pipeline**
1. **Frontend Sanitization**: Client-side input cleaning and validation
2. **Pydantic Validation**: Server-side model validation with type checking
3. **SQL Injection Prevention**: Query validation and parameterization
4. **XSS Protection**: HTML escaping and Content Security Policy

### **Authentication Flow**
1. **Password Hashing**: Bcrypt with 12 rounds for secure storage
2. **Session Management**: Secure HTTP-only cookies with CSRF protection
3. **Rate Limiting**: Configurable request throttling by IP and user
4. **Access Control**: Route-level authentication and authorization

### **Security Headers**
- **Content Security Policy**: Strict resource loading policies
- **HSTS**: HTTP Strict Transport Security for HTTPS enforcement
- **X-Frame-Options**: Clickjacking prevention
- **X-Content-Type-Options**: MIME type sniffing prevention
- **Referrer Policy**: Referrer information control

## Development Workflow

### **Code Quality Standards**
1. **Type Hints**: Full type annotation for all Python code
2. **Async/Await**: Consistent async patterns for I/O operations
3. **Error Handling**: Comprehensive exception handling with logging
4. **Testing**: Unit tests, integration tests, and security tests
5. **Documentation**: Docstrings and inline documentation

### **Frontend Development**
1. **Modular Architecture**: Component-based design with clear boundaries
2. **Security First**: Input sanitization and XSS prevention
3. **Accessibility**: WCAG compliance and semantic HTML
4. **Performance**: Lazy loading, code splitting, and optimization
5. **Progressive Enhancement**: Works without JavaScript enabled

### **Database Operations**
1. **Async Patterns**: All database operations use aiosqlite
2. **Connection Pooling**: Efficient connection management
3. **Schema Migrations**: Version-controlled schema changes
4. **Data Validation**: Input validation before database operations
5. **Backup Strategy**: Regular database backups and recovery procedures

## Integration Points

### **OpenAI Realtime API**
- **Connection**: WebSocket-based real-time communication
- **Function Tools**: Custom functions for database operations
- **Session Management**: Interview session isolation and tracking
- **Audio Processing**: 24kHz mono format for optimal quality

### **Judge0 API**
- **Code Execution**: Sandboxed environment for code testing
- **Language Support**: Multiple programming languages
- **Resource Limits**: Memory and time constraints for security
- **Result Processing**: Execution results, timing, and error handling

### **WebSocket Communication**
- **Session Isolation**: Unique session IDs for concurrent interviews
- **Event Handling**: Structured message passing and event processing
- **Error Recovery**: Connection resilience and automatic reconnection
- **Audio Streaming**: Real-time audio data transmission

## Monitoring and Observability

### **Logging Strategy**
- **Structured Logging**: JSON format for log aggregation
- **Log Levels**: Appropriate log levels for different components
- **Request Tracing**: Request IDs for distributed tracing
- **Error Tracking**: Comprehensive error logging and alerting

### **Performance Monitoring**
- **Database Queries**: Query performance and optimization
- **API Response Times**: Endpoint performance tracking
- **WebSocket Connections**: Connection count and health monitoring
- **Resource Usage**: Memory, CPU, and disk usage tracking

### **Security Monitoring**
- **Authentication Events**: Login attempts, failures, and successes
- **Rate Limiting**: Request rate monitoring and alerting
- **Input Validation**: Failed validation attempts and patterns
- **Error Patterns**: Security-related error pattern detection

## Production Deployment

### **Infrastructure Requirements**
- **Python 3.12+**: Modern Python version with async support
- **SQLite Database**: Lightweight database with backup strategy
- **HTTPS**: SSL/TLS encryption for all communications
- **Reverse Proxy**: nginx/Apache for static file serving and SSL termination

### **Configuration Management**
- **Environment Variables**: Secure configuration via environment
- **Secret Management**: API keys and secrets stored securely
- **Database Security**: File permissions and access controls
- **Monitoring**: Application and infrastructure monitoring

### **Deployment Strategy**
- **Blue-Green Deployment**: Zero-downtime deployments
- **Health Checks**: Application health monitoring
- **Rollback Procedures**: Quick rollback capabilities
- **Backup Strategy**: Regular data backups and recovery testing

---

## Development Best Practices

### **🛡️ Security-First Development**
1. **Input Validation**: Validate all inputs at multiple layers
2. **Output Encoding**: Proper encoding for all dynamic content
3. **Authentication**: Secure authentication and session management
4. **Authorization**: Proper access controls for all resources
5. **Logging**: Security event logging without sensitive data exposure

### **📦 Modular Architecture**
1. **Separation of Concerns**: Clear boundaries between components
2. **Dependency Injection**: Loose coupling through dependency injection
3. **Interface Design**: Well-defined interfaces between layers
4. **Code Reuse**: Shared utilities and common patterns
5. **Testing**: Unit tests for individual components

### **🚀 Performance Optimization**
1. **Async Operations**: Non-blocking I/O for all database and API calls
2. **Connection Pooling**: Efficient resource management
3. **Caching**: Strategic caching for frequently accessed data
4. **Lazy Loading**: Load resources only when needed
5. **Code Splitting**: Modular loading for frontend components

**Remember**: This is a production application handling sensitive interview data. Security, performance, and code quality are non-negotiable requirements.