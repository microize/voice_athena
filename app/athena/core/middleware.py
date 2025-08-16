"""Middleware for error handling and logging"""
import logging
import time
import uuid
from typing import Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from athena.core.exceptions import AthenaException

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle errors"""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            return response
            
        except AthenaException as e:
            logger.warning(
                f"Application error [{request_id}]: {e.message}",
                extra={
                    "request_id": request_id,
                    "error_code": e.error_code,
                    "details": e.details,
                    "path": str(request.url.path),
                    "method": request.method
                }
            )
            
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "message": e.message,
                        "code": e.error_code,
                        "details": e.details,
                        "request_id": request_id
                    }
                }
            )
            
        except HTTPException as e:
            logger.warning(
                f"HTTP error [{request_id}]: {e.detail}",
                extra={
                    "request_id": request_id,
                    "status_code": e.status_code,
                    "path": str(request.url.path),
                    "method": request.method
                }
            )
            
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "message": e.detail,
                        "code": f"HTTP_{e.status_code}",
                        "request_id": request_id
                    }
                }
            )
            
        except Exception as e:
            logger.error(
                f"Unexpected error [{request_id}]: {str(e)}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "path": str(request.url.path),
                    "method": request.method
                }
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": "Internal server error",
                        "code": "INTERNAL_ERROR",
                        "request_id": request_id
                    }
                }
            )

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response details"""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_id": getattr(request.state, "request_id", None)
            }
        )
        
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "request_id": getattr(request.state, "request_id", None)
            }
        )
        
        # Add request ID to response headers
        if hasattr(request.state, "request_id"):
            response.headers["X-Request-ID"] = request.state.request_id
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response