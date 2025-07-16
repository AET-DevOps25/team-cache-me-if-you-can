import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Header, Path, status
from app.services.document_service import (
    DocumentProcessingService,
    get_document_processing_service,
)
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentSourceResponse,
    TaskStatusResponse,
    DocumentDeleteResponse,
    DocumentTaskStatusResponse,
)
from app.celery_tasks.document_tasks import process_and_index_document_task
from typing import List
from celery.result import AsyncResult


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


@router.delete("/{source_filename}", response_model=DocumentDeleteResponse)
async def delete_document(
    source_filename: str = Path(..., description="The filename of the document to delete."),
    group_id: str = Header(..., alias="X-Group-ID"),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service),
):
    """
    Deletes a document and all its associated indexed data for a given group.
    """
    logger.info(f"Received request to delete document: {source_filename} for group: {group_id}")
    try:
        success, message = await doc_service.delete_document(source_filename, group_id)
        if not success and "not found" in message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)

        return DocumentDeleteResponse(filename=source_filename, message=message)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error deleting document {source_filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {source_filename}.")


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    group_id: str = Header(..., alias="X-Group-ID"),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service),
):
    """
    Endpoint to upload a document (PDF, DOCX, PPTX) for processing and indexing.
    """
    logger.info(f"Received request to /upload. Group-ID: {group_id}, Filename: {file.filename}, Content-Type: {file.content_type}")

    if not file.filename:
        logger.warning("Upload attempt with no filename.")
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
        logger.info(f"Read {len(contents)} bytes from uploaded file: {file.filename}")

        if not contents:
            logger.warning(f"File content is empty for {file.filename}. Aborting processing.")
            raise HTTPException(status_code=400, detail="Uploaded file content is empty.")

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


@router.get("/upload/status/{task_id}", response_model=DocumentTaskStatusResponse)
def get_upload_status(task_id: str):
    """
    Checks the status of a document processing and indexing task.
    """
    task_result = AsyncResult(task_id, app=process_and_index_document_task.app)

    result_data = task_result.result
    if task_result.failed():
        # Log the traceback if the task failed
        logger.error(f"Task {task_id} failed with error: {task_result.traceback}")
        # The result of a failed task is the exception object. Convert it to a string for the response.
        result_data = {"error_message": str(task_result.result), "docs_indexed": 0, "filename": ""}

    return DocumentTaskStatusResponse(
        task_id=task_id,
        status=task_result.status,
        result=result_data,
    )
