"""FastAPI application factory"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from athena.core.config import settings
from athena.core.database import init_database
from athena.core.logging_config import setup_logging, get_logger
from athena.core.middleware import (
    ErrorHandlingMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware
)
from athena.api import create_api_router

# Setup logging
setup_logging()
logger = get_logger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Athena application...")
    
    # Validate configuration
    settings.validate_config()
    
    # Initialize database
    await init_database()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Athena application...")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Create FastAPI app
    app = FastAPI(
        title="Athena Interview Platform",
        description="AI-powered coding interview platform with modular architecture",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # Add middleware (order matters - first added = outermost)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    api_router = create_api_router()
    app.include_router(api_router)
    
    # Mount static files last to avoid route conflicts
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    logger.info("FastAPI application created and configured")
    return app