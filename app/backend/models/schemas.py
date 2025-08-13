"""Pydantic models and schemas for the application."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# Request/Response models
class QueryRequest(BaseModel):
    """SQL query request model."""
    query: str


class LoginRequest(BaseModel):
    """User login request model."""
    username: str
    password: str


class SubmissionRequest(BaseModel):
    """Code submission request model."""
    source_code: str
    language_id: int


class RunCodeRequest(BaseModel):
    """Code execution request model."""
    source_code: str
    language_id: int
    test_input: str


# Domain models
class User(BaseModel):
    """User model."""
    username: str
    name: str
    email: Optional[str] = None


class Problem(BaseModel):
    """Problem model."""
    id: int
    title: str
    description: str
    examples: List[Dict[str, str]] = []
    constraints: List[str] = []
    difficulty: str  # 'Easy', 'Medium', 'Hard'
    category: str
    tags: List[str] = []
    test_cases: List[Dict[str, str]]
    solution_template: Dict[str, str] = {}
    acceptance_rate: float = 0.0
    created_at: Optional[datetime] = None


class ProblemListItem(BaseModel):
    """Problem list item model for listing problems."""
    id: int
    title: str
    difficulty: str
    category: str
    tags: List[str] = []
    acceptance_rate: float = 0.0


class TestCase(BaseModel):
    """Test case model."""
    input: str
    expected_output: str


class SolutionTemplate(BaseModel):
    """Solution template model."""
    language: str
    template: str


class Submission(BaseModel):
    """Submission model."""
    id: int
    user_id: str
    problem_id: int
    language_id: int
    source_code: str
    status: str
    runtime: Optional[float] = None
    memory_usage: Optional[int] = None
    judge0_token: Optional[str] = None
    submitted_at: datetime


class SubmissionResult(BaseModel):
    """Submission result model."""
    status: str
    accepted: bool
    runtime: Optional[float] = None
    memory: Optional[int] = None
    test_cases_passed: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None


class CodeExecutionResult(BaseModel):
    """Code execution result model."""
    status: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    time: Optional[float] = None
    memory: Optional[int] = None
    compile_output: Optional[str] = None


class UserProgress(BaseModel):
    """User progress model."""
    user_id: str
    problems_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_submissions: int = 0
    last_solved_at: Optional[datetime] = None


# Interview-related models
class InterviewSession(BaseModel):
    """Interview session model."""
    id: Optional[int] = None
    user_email: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    overall_score: Optional[float] = None


class InterviewQuestion(BaseModel):
    """Interview question model."""
    id: Optional[int] = None
    session_id: int
    question_text: str
    category: str
    difficulty: str
    timestamp: Optional[datetime] = None


class InterviewResponse(BaseModel):
    """Interview response model."""
    id: Optional[int] = None
    session_id: int
    question_id: int
    response_text: Optional[str] = None
    score: float
    feedback: Optional[str] = None
    timestamp: Optional[datetime] = None


class SessionReport(BaseModel):
    """Session report model."""
    id: Optional[int] = None
    session_id: int
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendations: Optional[str] = None
    overall_assessment: Optional[str] = None


# API Response models
class LoginResponse(BaseModel):
    """Login response model."""
    success: bool
    message: str
    user: Optional[User] = None


class QueryResponse(BaseModel):
    """Query response model."""
    results: List[List[Any]]
    columns: List[str]
    count: int


class ProblemsListResponse(BaseModel):
    """Problems list response model."""
    problems: List[ProblemListItem]


class LanguagesResponse(BaseModel):
    """Supported languages response model."""
    languages: Dict[str, int]


class UserStatusResponse(BaseModel):
    """User status response model."""
    user: Optional[User] = None
    authenticated: bool


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str