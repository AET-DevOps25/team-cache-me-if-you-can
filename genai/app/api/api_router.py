from fastapi import APIRouter
from app.api.endpoints import documents, chat

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])


# Health check endpoint
@api_router.get("/health", tags=["health"])
async def health_check():
    return {"status": "OK"}
