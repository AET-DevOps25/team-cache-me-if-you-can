from fastapi import FastAPI
from app.api.routes import api_router
from app.config import settings
from app.utils.logging_config import setup_logging
# from app.vector_store.weaviate_connector import init_weaviate_schema # Example for startup event

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI Service for StudySync: AI-Powered Collaborative Study Assistant"
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "message": f"{settings.APP_NAME} is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 