import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.api_router import api_router  # Corrected import
from app.config import settings
from app.utils.logging_config import (
    setup_logging,
)  # Assuming you have this for structured logging
from app.vector_store.weaviate_connector import (
    get_weaviate_client,
)  # For startup initialization

# Setup logging as early as possible
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    logger.info(f"Starting up {settings.APP_NAME}...")
    try:
        # Initialize Weaviate client and ensure schema exists on startup
        get_weaviate_client()
        logger.info("Weaviate client initialized and schema checked.")
    except Exception as e:
        logger.error(
            f"Failed to initialize Weaviate during startup: {e}", exc_info=True
        )
        # Depending on severity, you might want to prevent app startup or handle gracefully
    yield
    # Shutdown events
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI Service for StudySync: AI-Powered Collaborative Study Assistant",
    lifespan=lifespan,  # Use the new lifespan context manager
)

# Include the main API router
app.include_router(api_router, prefix="/api/v1")  # Added a version prefix


# Root path for basic info (optional)
@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": f"Welcome to {settings.APP_NAME}! Navigate to /docs for API documentation."
    }


# The health check is now part of api_router.py, so the one below can be removed or kept if desired at root.
# @app.get("/health", tags=["Health"])
# async def health_check():
#     """Basic health check endpoint."""
#     return {"status": "ok", "message": f"{settings.APP_NAME} is running!"}

if __name__ == "__main__":
    import uvicorn

    logger.info(
        f"Starting Uvicorn server for {settings.APP_NAME} on http://0.0.0.0:8000"
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)
