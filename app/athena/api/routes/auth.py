"""Authentication API routes"""
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from athena.models.schemas import LoginRequest, AuthResponse, UserResponse
from athena.core.security import SecurityManager, require_auth, get_current_user
from athena.core.config import settings

router = APIRouter(prefix="/api", tags=["authentication"])

@router.post("/login")
async def login(login_request: LoginRequest, response: Response):
    """Handle user login"""
    if SecurityManager.verify_user(login_request.username, login_request.password):
        # Create session
        session_token = SecurityManager.create_session(login_request.username)
        
        # Set secure HTTP-only cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "username": login_request.username
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
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