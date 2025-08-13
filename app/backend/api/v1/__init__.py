"""API v1 endpoints."""

from fastapi import APIRouter
from .problems import router as problems_router
from .auth import router as auth_router
from .users import router as users_router

api_router = APIRouter(prefix="/api")

api_router.include_router(problems_router, prefix="/problems", tags=["problems"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])

__all__ = ["api_router"]
