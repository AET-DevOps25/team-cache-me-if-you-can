from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class DocumentUploadResponse(BaseModel):
    filename: str
    message: str
    document_count: Optional[int] = None
    error: Optional[str] = None
    task_id: Optional[str] = None


class DocumentSourceResponse(BaseModel):
    source: str


class DocumentDeleteResponse(BaseModel):
    filename: str
    message: str


class DocumentResponse(BaseModel):
    filename: str
    metadata: Dict[str, Any]


class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = None
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


class QueryTaskResponse(BaseModel):
    task_id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[QueryResponse] = None


class DocumentProcessingResult(BaseModel):
    filename: str
    docs_indexed: int
    error_message: Optional[str] = None


class DocumentTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[DocumentProcessingResult] = None


class HealthCheckResponse(BaseModel):
    status: str = "OK"


# New schemas for handwritten document processing
class HandwrittenUploadResponse(BaseModel):
    task_id: str
    filename: str
    message: str
    error: Optional[str] = None


class HandwrittenDocument(BaseModel):
    task_id: str
    original_filename: str
    processed_filename: Optional[str] = None
    status: str  # PENDING, SUCCESS, FAILURE
    upload_timestamp: str
    group_id: str
    error_message: Optional[str] = None


class HandwrittenListResponse(BaseModel):
    processing: List[HandwrittenDocument]
    completed: List[HandwrittenDocument]


class HandwrittenStatusResponse(BaseModel):
    task_id: str
    status: str
    original_filename: str
    processed_filename: Optional[str] = None
    error_message: Optional[str] = None


class HandwrittenDeleteResponse(BaseModel):
    task_id: str
    message: str
