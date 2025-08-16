# Athena Interview Platform

🏗️ **Modular AI-Powered Coding Interview Platform**

## 🚀 Quick Start

### Run Application (Recommended)
```bash
python run_athena.py
# or directly:
uv run python -m athena.main
```

### Legacy Support
```bash
python run_athena.py --legacy
```

## 📁 Project Structure

```
athena/                       # Modular application structure
├── main.py                   # Application entry point
├── core/                     # Core application modules
│   ├── app.py               # FastAPI application factory
│   ├── config.py            # Configuration management
│   ├── security.py          # Authentication & authorization
│   ├── database.py          # Database operations
│   ├── dependencies.py      # Dependency injection container
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── middleware.py        # Error handling & logging middleware
│   └── logging_config.py    # Logging configuration
├── api/                     # API routes
│   ├── __init__.py         # API router factory
│   └── routes/             # Organized route modules
│       ├── auth.py         # Authentication routes
│       ├── problems.py     # Problem management routes
│       ├── database.py     # Database query routes
│       ├── interview.py    # Interview session routes
│       ├── websockets.py   # WebSocket routes
│       └── pages.py        # Static page routes
├── services/               # Business logic layer
│   ├── problem_service.py  # Problem database operations
│   ├── user_service.py     # User management operations
│   └── interview_service.py # Interview session operations
├── models/                 # Data models and schemas
│   └── schemas.py         # Pydantic data models
└── utils/                 # Utility functions
    └── __init__.py
```

## ✨ Key Features

### 🏗️ Modular Architecture
- **Clean separation of concerns** following Python best practices
- **Dependency injection** for testable and maintainable code
- **Service layer pattern** for business logic separation
- **Comprehensive error handling** with custom exception hierarchy

### 🔒 Security & Authentication
- **Multi-method authentication** (cookies, Bearer tokens, Basic auth)
- **Session management** with expiration and cleanup
- **Security middleware** with proper headers and validation
- **Password hashing** with salt for secure storage

### 📊 Observability
- **Structured logging** with file rotation and levels
- **Request tracking** with unique request IDs
- **Error monitoring** with contextual information
- **Performance metrics** and duration tracking

### 🔧 Configuration Management
- **Environment-based configuration** with validation
- **Type-safe settings** with defaults and validation
- **Centralized configuration** for easy maintenance

## 🛠️ Development

### Adding New Features
1. **API Routes**: Add to `athena/api/routes/`
2. **Business Logic**: Add to `athena/services/`
3. **Data Models**: Update `athena/models/schemas.py`
4. **Configuration**: Update `athena/core/config.py`

### Testing
The modular structure makes testing easy with dependency injection:
```python
from athena.core.dependencies import get_problem_service
# Services are easily mockable for unit tests
```

## 📚 Documentation

- **Setup Guide**: [`docs/SETUP_CODING_PLATFORM.md`](docs/SETUP_CODING_PLATFORM.md)
- **Architecture**: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Interview Fixes**: [`docs/INTERVIEW_FIXES.md`](docs/INTERVIEW_FIXES.md)

## 🔧 Utilities

- **Database Scripts**: `scripts/` - Utility scripts for database management
- **Application Runner**: `run_athena.py` - Unified application launcher
- **Legacy Backup**: `server.py.backup` - Original monolithic version

## 🎯 Access Points

- **Main Application**: http://localhost:8003/
- **Login Page**: http://localhost:8003/login
- **Problems List**: http://localhost:8003/problems
- **Database Interface**: http://localhost:8003/database

## 🔑 Default Credentials

- `admin` / `password123`
- `demo` / `demo123`

---

Built with ❤️ using FastAPI, SQLite, and modern Python best practices.