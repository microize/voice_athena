"""Static page routes"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path
from athena.core.security import require_auth, get_current_user

router = APIRouter(tags=["pages"])

# Define static file paths
STATIC_DIR = Path("static")

@router.get("/")
async def root(request: Request):
    """Redirect to login if not authenticated, otherwise serve dashboard"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/interview")
async def interview_page(user = Depends(require_auth)):
    """Serve the interview page"""
    return FileResponse(STATIC_DIR / "index.html")

@router.get("/login")
async def login_page():
    """Serve the login page"""
    return FileResponse(STATIC_DIR / "login.html")

@router.get("/problems")
async def problems_page(user = Depends(require_auth)):
    """Serve the problems list page"""
    return FileResponse(STATIC_DIR / "problems.html")

@router.get("/problem/{problem_id}")
async def problem_page(problem_id: int, user = Depends(require_auth)):
    """Serve the individual problem page"""
    return FileResponse(STATIC_DIR / "problem.html")

@router.get("/dashboard")
async def dashboard_page(user = Depends(require_auth)):
    """Serve the dashboard page"""
    return FileResponse(STATIC_DIR / "dashboard.html")

@router.get("/database")
async def database_page(user = Depends(require_auth)):
    """Serve the database query page"""
    return FileResponse(STATIC_DIR / "database.html")