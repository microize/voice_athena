"""Pydantic models and schemas"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# Enums for better type safety
class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium" 
    HARD = "Hard"

class ProblemCategory(str, Enum):
    ARRAY = "Array"
    STRING = "String"
    HASH_TABLE = "Hash Table"
    DYNAMIC_PROGRAMMING = "Dynamic Programming"
    MATH = "Math"
    TREE = "Tree"
    GRAPH = "Graph"
    SQL = "SQL"

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Request Models
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)

class RunCodeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000)
    language: str = Field(..., min_length=1, max_length=20)
    input: str = Field(default="", max_length=10000)

class SubmissionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000)
    language: str = Field(..., min_length=1, max_length=20)

# Response Models
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None

class UserResponse(BaseModel):
    username: str
    session_token: Optional[str] = None

class ProblemListItem(BaseModel):
    id: int
    title: str
    difficulty: DifficultyLevel
    category: ProblemCategory
    tags: List[str]
    acceptance_rate: Optional[float] = None

class ProblemDetail(BaseModel):
    id: int
    title: str
    description: str
    examples: List[Dict[str, Any]]
    constraints: List[str]
    difficulty: DifficultyLevel
    category: ProblemCategory
    tags: List[str]
    test_cases: Dict[str, Any]
    solution_template: Dict[str, str]

class SubmissionResult(BaseModel):
    id: Optional[str] = None
    status: SubmissionStatus
    time: Optional[float] = None
    memory: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    message: Optional[str] = None

class UserProgress(BaseModel):
    problems_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_submissions: int = 0
    last_solved_at: Optional[datetime] = None

class InterviewSession(BaseModel):
    session_id: str
    employee_id: Optional[str] = None
    start_time: datetime
    status: str = "active"

# Database Models
class Problem(BaseModel):
    """Database model for problems"""
    id: Optional[int] = None
    title: str
    description: str
    examples: str  # JSON string
    constraints: str  # JSON string
    difficulty: str
    category: str
    tags: str  # JSON string
    test_cases: str  # JSON string
    solution_template: str  # JSON string
    acceptance_rate: Optional[float] = 85.5
    created_at: Optional[datetime] = None

class Submission(BaseModel):
    """Database model for submissions"""
    id: Optional[int] = None
    problem_id: int
    code: str
    language: str
    status: str
    runtime: Optional[int] = None
    memory: Optional[int] = None
    created_at: Optional[datetime] = None

# Validation
class ValidatedQueryRequest(QueryRequest):
    @validator('query')
    def validate_sql_query(cls, v):
        # Basic SQL validation - only allow SELECT, WITH, PRAGMA
        v_upper = v.upper().strip()
        allowed_starts = ('SELECT', 'WITH', 'PRAGMA')
        
        if not any(v_upper.startswith(start) for start in allowed_starts):
            raise ValueError('Only SELECT, WITH, and PRAGMA statements are allowed')
        
        # Block dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'TRUNCATE']
        if any(keyword in v_upper for keyword in dangerous_keywords):
            raise ValueError('Dangerous SQL operations are not allowed')
        
        return v