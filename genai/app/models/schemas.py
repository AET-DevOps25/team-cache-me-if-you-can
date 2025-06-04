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


class DocumentMetadata(BaseModel):
    source: str
    page_number: Optional[int] = None
    # You can add other relevant metadata fields here, e.g., document_id, chunk_id, score


class SourceDocument(BaseModel):
    page_content: str
    metadata: DocumentMetadata


class QueryResponse(BaseModel):
    answer: str
    source_documents: Optional[List[SourceDocument]] = None  # Updated to use SourceDocument
    error: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str = "OK"
