# Contributing to Athena Voice Interview Platform

Thank you for your interest in contributing to Athena! This document provides guidelines for contributing to this production-grade voice interview platform that handles sensitive interview data.

## 🚨 Security First Contribution Policy

**⚠️ CRITICAL**: This application handles sensitive interview data and employee information. All contributions MUST follow security-first principles.

### **Security Review Required**
- All code changes undergo mandatory security review
- No exceptions for security standards compliance
- Contributions that compromise security will be rejected immediately

## 🎯 Contribution Areas

### **High Priority Areas**
- 🔒 **Security Enhancements**: Authentication, validation, rate limiting
- 🏗️ **Modular Architecture**: Component isolation and code organization
- 🧪 **Testing Coverage**: Unit, integration, and security tests
- 📊 **Performance Optimization**: Database queries, WebSocket efficiency
- 📖 **Documentation**: API docs, security guides, architecture

### **Feature Contributions**
- 🎤 **Interview System**: AI agent improvements, question categories
- 📈 **Analytics**: Performance metrics, reporting enhancements
- 💻 **Coding Platform**: Problem sets, evaluation algorithms
- 🎨 **User Interface**: Accessibility, responsive design
- 🔧 **Developer Tools**: Debugging, monitoring, deployment

## 🛠️ Development Environment Setup

### **Prerequisites**
```bash
# Required Tools
- Python 3.12+
- UV package manager (astral.sh/uv)
- Git with SSH keys configured
- OpenAI API key with Realtime API access
- Code editor with Python and JavaScript support
```

### **Local Setup**
```bash
# 1. Fork and Clone
git clone git@github.com:your-username/athena.git
cd athena/app/

# 2. Environment Setup
uv sync                          # Install dependencies
cp .env.example .env            # Create environment file
# Edit .env with your OpenAI API key

# 3. Database Initialization
uv run python scripts/update_sql_schemas.py

# 4. Development Server
uv run python run_athena.py     # Start on http://localhost:8000

# 5. Verify Setup
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### **Development Tools**
```bash
# Code Quality Tools
uv run black athena/            # Code formatting
uv run isort athena/            # Import sorting
uv run mypy athena/             # Type checking
uv run bandit -r athena/        # Security scanning

# Testing Suite
uv run pytest                   # All tests
uv run pytest tests/security/   # Security tests only
uv run pytest --cov=athena     # Coverage report
```

## 📋 Contribution Process

### **1. Issue Selection**
- Browse [GitHub Issues](link-to-issues) for open tasks
- Comment on issues you'd like to work on
- Wait for maintainer assignment before starting work
- For new features, create an issue first for discussion

### **2. Development Workflow**
```bash
# Create Feature Branch
git checkout -b feature/your-feature-name
git checkout -b security/fix-description
git checkout -b docs/update-area

# Development Process
# - Follow architectural patterns
# - Write tests for new code
# - Update documentation
# - Run quality checks

# Commit Standards
git commit -m "feat: add user authentication rate limiting

- Implement sliding window rate limiting
- Add Redis backend for distributed limiting  
- Update security tests for rate limit scenarios
- Document rate limiting configuration

Fixes #123"
```

### **3. Pull Request Process**
```markdown
## Pull Request Template

### Description
Brief description of changes and motivation

### Type of Change
- [ ] 🔒 Security enhancement
- [ ] 🐛 Bug fix (non-breaking change)
- [ ] ✨ New feature (non-breaking change)
- [ ] 💥 Breaking change (fix or feature causing existing functionality to change)
- [ ] 📖 Documentation update
- [ ] 🧪 Test improvements

### Security Checklist
- [ ] No hardcoded secrets or API keys
- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] Authentication/authorization checked
- [ ] Rate limiting considered
- [ ] Security headers configured
- [ ] Error messages don't leak sensitive info

### Modular Architecture Checklist  
- [ ] No duplicate CSS rules across files
- [ ] JavaScript utilities in utils.js
- [ ] CSS variables in global.css
- [ ] Component styles self-contained
- [ ] No inline styles or scripts
- [ ] Proper dependency loading order

### Testing
- [ ] Unit tests written/updated
- [ ] Integration tests pass
- [ ] Security tests included
- [ ] Test coverage maintained >80%
- [ ] Manual testing completed

### Documentation
- [ ] Code comments added/updated
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] CHANGELOG entry added
```

## 🏗️ Architecture Guidelines

### **Frontend Development**

#### **Component Creation**
```html
<!-- components/new-component.html -->
<div class="new-component">
    <div class="component-header">
        <h3>Component Title</h3>
    </div>
    <div class="component-content">
        <!-- Component content -->
    </div>
</div>
```

```css
/* components/new-component.css */
.new-component {
    /* Use CSS variables from global.css */
    background: var(--screen);
    border-radius: var(--radius-lg);
    padding: 20px;
}

.component-header {
    margin-bottom: 16px;
    color: var(--foreground);
}

/* Responsive design */
@media (max-width: 768px) {
    .new-component {
        padding: 12px;
    }
}
```

```javascript
// components/new-component.js
class NewComponent {
    constructor() {
        this.initialized = false;
    }
    
    async load(config = {}) {
        if (this.initialized) return;
        
        try {
            await this.init(config);
            this.initialized = true;
        } catch (error) {
            console.error('Component load failed:', error);
        }
    }
    
    async init(config) {
        // Component initialization
        this.setupEventListeners();
        this.loadData(config);
    }
    
    setupEventListeners() {
        // Event handling
    }
    
    async loadData(config) {
        // Data loading logic
    }
}

// Global registration
window.NewComponent = new NewComponent();
```

#### **CSS Architecture Standards**
```css
/* Use global.css for shared styles */
:root {
    --new-color: #value;        /* Add new CSS variables */
}

/* Component-specific styles only */
.component-specific-class {
    /* Unique styles for this component */
}

/* No duplicate rules - check existing files first */
/* No inline styles in HTML */
/* Use semantic class names */
```

#### **JavaScript Standards**
```javascript
// utils.js - Shared utilities only
function newUtility(input) {
    // Sanitize input
    const sanitized = sanitizeInput(input);
    
    // Validate
    if (!sanitized) {
        throw new Error('Invalid input');
    }
    
    return sanitized;
}

// Export for global use
window.newUtility = newUtility;

// page-specific.js - Page logic only
document.addEventListener('DOMContentLoaded', async () => {
    // Use shared utilities
    await loadNavigation({activePage: 'page-name'});
    
    // Page-specific initialization
    initializePageFeatures();
});
```

### **Backend Development**

#### **Service Layer Pattern**
```python
# services/new_service.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.schemas import RequestModel, ResponseModel
from ..core.exceptions import BusinessLogicError

class NewService:
    """
    Business logic service for [domain area].
    
    Security Considerations:
    - All inputs validated through Pydantic models
    - Database queries use parameterized statements
    - Sensitive operations logged for audit
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, request: RequestModel) -> ResponseModel:
        """
        Create new entity with validation and security checks.
        
        Args:
            request: Validated request model
            
        Returns:
            ResponseModel with created entity
            
        Raises:
            ValidationError: Invalid input data
            SecurityError: Permission denied
            DatabaseError: Database operation failed
        """
        # Validate business rules
        await self._validate_creation(request)
        
        # Perform operation
        entity = await self._create_entity(request)
        
        # Log for audit
        logger.info(f"Entity created: {entity.id}")
        
        return ResponseModel(data=entity)
    
    async def _validate_creation(self, request: RequestModel):
        """Private validation method"""
        # Business rule validation
        pass
    
    async def _create_entity(self, request: RequestModel):
        """Private creation method"""
        # Database operation
        pass
```

#### **API Route Standards**
```python
# api/routes/new_endpoint.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from ..services.new_service import NewService
from ..models.schemas import RequestModel, ResponseModel
from ..core.dependencies import get_new_service, get_current_user
from ..core.security import require_permission

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/new", tags=["new"])

@router.post(
    "/create",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create new entity",
    description="""
    Create a new entity with proper validation and security.
    
    **Security:**
    - Authentication required
    - Rate limited to 10 requests per minute
    - Input validation with Pydantic
    - Permission-based access control
    
    **Process:**
    1. Validate authentication token
    2. Check user permissions
    3. Validate request data
    4. Create entity with audit logging
    """
)
@limiter.limit("10/minute")
async def create_entity(
    request: RequestModel,
    current_user: User = Depends(get_current_user),
    service: NewService = Depends(get_new_service)
):
    """Create new entity endpoint"""
    try:
        # Permission check
        require_permission(current_user, "entity.create")
        
        # Business logic
        result = await service.create(request)
        
        return result
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e}"
        )
    except SecurityError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

#### **Database Model Standards**
```python
# models/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class NewRequestModel(BaseModel):
    """
    Request model for new entity creation.
    
    Security Validations:
    - Input length restrictions
    - Content sanitization
    - Format validation
    """
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Entity name (1-100 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Optional description (max 5000 characters)"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name format and content"""
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Sanitize description content"""
        if v:
            # Remove potentially dangerous content
            sanitized = re.sub(r'[<>&"\'()]', '', v)
            return sanitized.strip()
        return v

class NewResponseModel(BaseModel):
    """Response model for entity operations"""
    
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## 🧪 Testing Standards

### **Test Structure Requirements**
```python
# tests/test_new_feature.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from athena.services.new_service import NewService
from athena.models.schemas import NewRequestModel

class TestNewFeature:
    """
    Comprehensive test suite for new feature.
    
    Test Categories:
    - Unit tests: Individual function testing
    - Integration tests: API endpoint testing  
    - Security tests: Authentication and validation
    - Edge cases: Error conditions and limits
    """
    
    async def test_create_entity_success(self, db_session: AsyncSession):
        """Test successful entity creation"""
        # Arrange
        service = NewService(db_session)
        request = NewRequestModel(name="Test Entity")
        
        # Act
        result = await service.create(request)
        
        # Assert
        assert result.name == "Test Entity"
        assert result.id is not None
    
    async def test_create_entity_validation_error(self, db_session: AsyncSession):
        """Test validation error handling"""
        service = NewService(db_session)
        
        with pytest.raises(ValidationError):
            await service.create(NewRequestModel(name=""))
    
    async def test_api_authentication_required(self, client: AsyncClient):
        """Test API authentication requirement"""
        response = await client.post("/api/new/create", json={})
        assert response.status_code == 401
    
    async def test_api_rate_limiting(self, client: AsyncClient, auth_headers):
        """Test API rate limiting"""
        # Make requests up to limit
        for _ in range(10):
            response = await client.post(
                "/api/new/create", 
                json={"name": "test"}, 
                headers=auth_headers
            )
        
        # Next request should be rate limited
        response = await client.post(
            "/api/new/create",
            json={"name": "test"},
            headers=auth_headers
        )
        assert response.status_code == 429
    
    async def test_sql_injection_prevention(self, client: AsyncClient, auth_headers):
        """Test SQL injection prevention"""
        malicious_input = "'; DROP TABLE users; --"
        response = await client.post(
            "/api/new/create",
            json={"name": malicious_input},
            headers=auth_headers
        )
        # Should either sanitize or reject
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            assert "DROP TABLE" not in response.json()["name"]
```

### **Security Test Requirements**
```python
# tests/security/test_authentication.py
class TestAuthentication:
    """Security-focused authentication tests"""
    
    async def test_password_hashing_strength(self):
        """Test bcrypt password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Verify bcrypt format
        assert hashed.startswith("$2b$")
        
        # Verify rounds (should be 12+)
        rounds = int(hashed.split("$")[2])
        assert rounds >= 12
    
    async def test_session_security(self, client: AsyncClient):
        """Test session cookie security"""
        response = await client.post("/api/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        
        # Check secure cookie flags
        set_cookie = response.headers["set-cookie"]
        assert "HttpOnly" in set_cookie
        assert "Secure" in set_cookie
        assert "SameSite=Strict" in set_cookie
    
    async def test_brute_force_protection(self, client: AsyncClient):
        """Test brute force protection"""
        # Attempt multiple failed logins
        for _ in range(6):
            await client.post("/api/auth/login", json={
                "username": "test_user",
                "password": "wrong_password"
            })
        
        # Should be rate limited
        response = await client.post("/api/auth/login", json={
            "username": "test_user", 
            "password": "correct_password"
        })
        assert response.status_code == 429
```

## 📖 Documentation Standards

### **Code Documentation**
```python
def complex_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Brief description of function purpose.
    
    Detailed explanation of what the function does, including:
    - Key business logic
    - Security considerations  
    - Performance implications
    
    Args:
        param1: Description of first parameter and constraints
        param2: Description of optional parameter with default behavior
        
    Returns:
        Dictionary containing:
        - key1: Description of return value structure
        - key2: Additional return value information
        
    Raises:
        ValidationError: When input validation fails
        SecurityError: When security checks fail
        DatabaseError: When database operations fail
        
    Security:
        - Input is validated and sanitized
        - Database queries use parameterized statements
        - Sensitive operations are logged
        
    Example:
        >>> result = complex_function("valid_input", 42)
        >>> print(result["key1"])
        expected_output
    """
```

### **API Documentation**
```python
@router.post(
    "/endpoint",
    response_model=ResponseModel,
    summary="Brief endpoint description",
    description="""
    Comprehensive endpoint description including:
    
    **Purpose:** What this endpoint accomplishes
    
    **Process:**
    1. Step-by-step process description
    2. Security validations performed
    3. Business logic applied
    4. Response generation
    
    **Security:**
    - Authentication requirements
    - Permission levels needed
    - Rate limiting applied
    - Input validation performed
    
    **Example Request:**
    ```json
    {
        "field1": "example_value",
        "field2": 123
    }
    ```
    
    **Example Response:**
    ```json
    {
        "id": 1,
        "status": "success",
        "data": {...}
    }
    ```
    """,
    responses={
        201: {"description": "Success response description"},
        400: {"description": "Validation error description"},
        401: {"description": "Authentication required"},
        403: {"description": "Permission denied"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
```

## 🔍 Code Review Process

### **Review Checklist**
```markdown
## Security Review
- [ ] No hardcoded secrets or credentials
- [ ] Input validation on all user inputs (frontend + backend)
- [ ] SQL injection prevention implemented
- [ ] XSS prevention in frontend code
- [ ] Authentication required for protected endpoints
- [ ] Authorization checks for sensitive operations
- [ ] Rate limiting on appropriate endpoints
- [ ] Security headers properly configured
- [ ] Error messages don't leak sensitive information
- [ ] Logging doesn't capture sensitive data

## Architecture Review
- [ ] Modular design principles followed
- [ ] No code duplication across components
- [ ] Proper separation of concerns (API/Service/Model layers)
- [ ] Component isolation maintained
- [ ] CSS variables used from global.css
- [ ] JavaScript utilities in utils.js
- [ ] No inline styles or scripts
- [ ] Proper dependency loading order

## Code Quality Review
- [ ] Type hints used throughout Python code
- [ ] Async/await patterns followed correctly
- [ ] Error handling comprehensive and appropriate
- [ ] Naming conventions consistent
- [ ] Functions and classes have single responsibility
- [ ] Performance considerations addressed
- [ ] Memory leaks prevented

## Testing Review
- [ ] Unit tests cover business logic
- [ ] Integration tests cover API endpoints
- [ ] Security tests included for new features
- [ ] Test coverage maintained above 80%
- [ ] Edge cases and error conditions tested
- [ ] Mocking used appropriately
- [ ] Tests are deterministic and independent

## Documentation Review
- [ ] Code properly documented with docstrings
- [ ] API changes reflected in OpenAPI docs
- [ ] README updated if necessary
- [ ] Security implications documented
- [ ] Breaking changes highlighted
- [ ] Examples provided for complex features
```

### **Review Timeline**
- **Initial Review**: Within 2 business days
- **Security Review**: Additional 1-2 days for security-sensitive changes
- **Final Approval**: After all feedback addressed and tests pass

## 🚀 Release Process

### **Version Management**
```bash
# Semantic Versioning (MAJOR.MINOR.PATCH)
# MAJOR: Breaking changes or security updates
# MINOR: New features, backwards compatible
# PATCH: Bug fixes, security patches

# Release Branch
git checkout -b release/v1.2.0
git tag v1.2.0
git push origin v1.2.0
```

### **Changelog Requirements**
```markdown
## [1.2.0] - 2024-01-15

### 🔒 Security
- Enhanced rate limiting with Redis backend
- Added CSRF protection for state-changing operations
- Improved session management with secure cookies

### ✨ Added
- New coding problems interface with syntax highlighting
- Real-time performance dashboard with metrics
- Enhanced AI agent with improved question categorization

### 🔧 Changed
- Upgraded to Python 3.12 for performance improvements
- Refactored frontend to pure modular architecture
- Optimized database queries for better performance

### 🐛 Fixed
- Fixed WebSocket connection stability issues
- Resolved authentication race conditions
- Corrected CSS variable inheritance

### 💥 Breaking Changes
- API endpoint `/api/v1/interview` moved to `/api/interview`
- Configuration format changed for security settings
- Database schema updated (migration script provided)
```

## 🤝 Community Guidelines

### **Code of Conduct**
- **Professional**: Maintain professional communication
- **Respectful**: Respect all contributors regardless of experience level
- **Collaborative**: Work together to improve security and functionality
- **Learning-Focused**: Help others learn and grow

### **Communication Channels**
- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and reviews
- **Discussions**: Architecture and design conversations
- **Security**: Private security issue reporting

### **Recognition**
- Contributors are recognized in CHANGELOG and release notes
- Significant contributions acknowledged in project documentation
- Security researchers credited for responsible disclosure

---

By contributing to Athena, you're helping build a secure, production-grade platform for voice-based technical interviews. Thank you for your commitment to security and quality!