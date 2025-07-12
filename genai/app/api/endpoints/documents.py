import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Header
from app.services.document_service import (
    DocumentProcessingService,
    get_document_processing_service,
)
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentSourceResponse,
    TaskStatusResponse,
)
from app.celery_tasks.document_tasks import process_and_index_document_task
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[DocumentSourceResponse])
def list_indexed_documents(
    group_id: str = Header(..., alias="X-Group-ID"),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service),
):
    """
    Lists all unique documents that have been indexed for a given group.
    """
    logger.info(f"Received request to list documents for group: {group_id}")
    try:
        # This returns a list of source strings
        source_names = doc_service.get_all_documents(group_id)
        # We need to map this to the response model
        documents = [{"source": name} for name in source_names]
        return documents
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve documents.")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    group_id: str = Header(..., alias="X-Group-ID"),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service),
):
    """
    Endpoint to upload a document (PDF, DOCX, PPTX) for processing and indexing.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")

    allowed_extensions = {".pdf", ".docx", ".pptx"}
    file_extension = "None"
    if "." in file.filename:
        file_extension = file.filename.rsplit(".", 1)[1].lower()
        if f".{file_extension}" not in allowed_extensions:
            logger.warning(f"Upload attempt with unsupported file type: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: '{file_extension}'. Supported types are PDF, DOCX, PPTX.",
            )
    else:
        logger.warning(f"Upload attempt with no file extension: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="File has no extension. Supported types are PDF, DOCX, PPTX.",
        )

    try:
        logger.info(f"Received file for upload: {file.filename} with group_id: {group_id}")
        contents = await file.read()

        task = process_and_index_document_task.delay(contents, file.filename, group_id)
        logger.info(f"Started Celery task {task.id} for {file.filename} in group {group_id}")

        return DocumentUploadResponse(
            filename=file.filename,
            message="Document uploaded and processing started in background.",
            task_id=task.id,
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(
            f"Unexpected error during file upload of {file.filename}: {e}",
            exc_info=True,
        )
        return DocumentUploadResponse(
            filename=file.filename,
            message="An unexpected server error occurred.",
            error=str(e),
        )
    finally:
        await file.close()
