"""Main FastAPI application entry point"""
import logging
import uvicorn
from athena.core.app import create_app
from athena.core.config import settings

# Create the app instance
app = create_app()
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    logger.info(f"Starting Athena server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "athena.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()