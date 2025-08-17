"""Authentication API routes"""
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from athena.models.schemas import LoginRequest, AuthResponse, UserResponse
from athena.core.security import SecurityManager, require_auth, get_current_user
from athena.core.config import settings

router = APIRouter(prefix="/api", tags=["authentication"])

@router.post("/login")
async def login(login_request: LoginRequest, request: Request, response: Response):
    """Handle user login with enhanced security"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting check
    if not SecurityManager.check_rate_limit(client_ip, max_requests=10, window=3600):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": "3600"}
        )
    
    if SecurityManager.verify_user(login_request.username, login_request.password, client_ip):
        # Create session
        session_token = SecurityManager.create_session(login_request.username)
        
        # Set secure HTTP-only cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60,
            httponly=True,
            secure=not settings.DEBUG,  # Only secure in production
            samesite="strict",  # Prevent CSRF
            domain=None  # Don't allow subdomain access
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "username": login_request.username
            }
        }
    else:
        # Don't reveal whether username exists
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Handle user logout"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        SecurityManager.invalidate_session(session_token)
    
    # Clear cookie
    response.delete_cookie("session_token")
    
    return {"success": True, "message": "Logged out successfully"}

@router.get("/user")
async def get_user(request: Request):
    """Get current user information"""
    user = get_current_user(request)
    if user:
        return {"user": {"username": user["username"]}, "authenticated": True}
    else:
        return {"user": None, "authenticated": False}