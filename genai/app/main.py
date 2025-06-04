import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.api_router import api_router  # Corrected import
from app.config import settings
from app.utils.logging_config import (
    setup_logging,
)
from app.vector_store.weaviate_connector import (
    get_weaviate_client,
)

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting up {settings.APP_NAME}...")
    try:
        get_weaviate_client()
        logger.info("Weaviate client initialized and schema checked.")
    except Exception as e:
        logger.error(f"Failed to initialize Weaviate during startup: {e}", exc_info=True)
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI Service for StudySync: AI-Powered Collaborative Study Assistant",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}! Navigate to /docs for API documentation."}


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting Uvicorn server for {settings.APP_NAME} on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
