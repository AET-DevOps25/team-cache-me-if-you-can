from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class DocumentUploadResponse(BaseModel):
    filename: str
    message: str
    document_count: Optional[int] = None
    error: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    # session_id: Optional[str] = None # For chat history if needed later


class QueryResponse(BaseModel):
    answer: str
    source_documents: Optional[List[Dict[str, Any]]] = (
        None  # To hold excerpts of source docs
    )
    error: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str = "OK"
