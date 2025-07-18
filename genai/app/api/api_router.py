from fastapi import APIRouter
from app.api.endpoints import documents, chat, doc_processing, summarization, handwritten

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(doc_processing.router, prefix="/doc_processing", tags=["doc_processing"])
api_router.include_router(summarization.router, prefix="/summaries", tags=["summarization"])
api_router.include_router(handwritten.router, prefix="/handwritten", tags=["handwritten"])


# Health check endpoint
@api_router.get("/health", tags=["health"])
async def health_check():
    return {"status": "OK"}
