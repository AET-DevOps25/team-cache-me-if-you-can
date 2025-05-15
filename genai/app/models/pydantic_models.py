from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatQuery(BaseModel):
    text: str = Field(..., description="The user's query text.", min_length=1)
    # group_id: Optional[str] = Field(None, description="Identifier for the study group context.")
    # user_id: Optional[str] = Field(None, description="Identifier for the user making the query.")
    # conversation_id: Optional[str] = Field(None, description="ID for an ongoing conversation thread.")

class ChatResponseSource(BaseModel):
    document_id: str = Field(..., description="ID of the source document.")
    source_name: str = Field(..., description="Filename or title of the source.")
    # page_number: Optional[int] = Field(None, description="Page number if applicable.")
    # relevance_score: Optional[float] = Field(None, description="Score from retriever.")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="The AI-generated answer to the query.")
    sources: List[ChatResponseSource] = Field([], description="List of sources used to generate the answer.")
    # conversation_id: Optional[str] = Field(None, description="ID for the conversation thread.")
    # error_message: Optional[str] = Field(None, description="Error message if query processing failed.")

class DocumentUploadResponse(BaseModel):
    message: str = Field(..., description="Status message of the upload.")
    document_id: str = Field(..., description="Unique identifier for the uploaded and processing document.")
    filename: str = Field(..., description="Original filename of the uploaded document.")

class DocumentStatus(BaseModel):
    status: str = Field(..., description="Processing status of the document (e.g., PENDING, PROCESSING, COMPLETED, FAILED).")
    message: Optional[str] = Field(None, description="Additional details about the status.")
    # num_chunks: Optional[int] = Field(None, description="Number of chunks generated if processing is complete.")
    # indexed_at: Optional[str] = Field(None, description="Timestamp of when indexing was completed.")

class DocumentStatusResponse(BaseModel):
    document_id: str = Field(..., description="Identifier of the document.")
    status_info: DocumentStatus = Field(..., description="Detailed status of the document.")

class WeaviateDocument(BaseModel):
    text_content: str
    source_filename: str
    group_id: str

# Generic error model for API responses
class ErrorDetail(BaseModel):
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail 