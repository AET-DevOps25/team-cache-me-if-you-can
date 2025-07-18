import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Header, Path, status
from fastapi.responses import FileResponse
from app.models.schemas import HandwrittenUploadResponse, HandwrittenListResponse, HandwrittenStatusResponse, HandwrittenDeleteResponse, HandwrittenDocument
from app.celery_tasks.document_tasks import process_handwritten_document_task
from app.services.handwritten_storage import get_handwritten_storage, HandwrittenDocumentStorage
from celery.result import AsyncResult
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=HandwrittenUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_handwritten_document(
    file: UploadFile = File(...),
    group_id: str = Header(..., alias="X-Group-ID"),
    storage: HandwrittenDocumentStorage = Depends(get_handwritten_storage),
):
    """
    Upload a handwritten PDF document for processing to LaTeX.
    """
    logger.info(f"Received handwritten document upload: {file.filename} for group {group_id}")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for handwritten document processing.")

    try:
        # Read file content
        contents = await file.read()
        logger.info(f"Read {len(contents)} bytes from uploaded file: {file.filename}")

        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file content is empty.")

        # Start Celery task first to get the real task ID
        task = process_handwritten_document_task.delay(contents, file.filename, group_id, None)

        # Use the Celery task ID for storage
        celery_task_id = task.id

        # Store metadata using the Celery task ID
        storage.store_document_metadata(celery_task_id, group_id, file.filename)

        logger.info(f"Started handwritten processing task {celery_task_id} for {file.filename} in group {group_id}")

        return HandwrittenUploadResponse(task_id=celery_task_id, filename=file.filename, message="Handwritten document uploaded and processing started in background.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error during handwritten document upload of {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")
    finally:
        await file.close()


@router.get("/", response_model=HandwrittenListResponse)
def list_handwritten_documents(
    group_id: str = Header(..., alias="X-Group-ID"),
    storage: HandwrittenDocumentStorage = Depends(get_handwritten_storage),
):
    """
    List all handwritten documents for a group, separated by processing status.
    """
    logger.info(f"Listing handwritten documents for group {group_id}")

    try:
        documents = storage.get_documents_by_group(group_id)

        processing = [doc for doc in documents if doc.status in ["PENDING", "PROCESSING"]]
        completed = [doc for doc in documents if doc.status in ["SUCCESS", "FAILURE"]]

        return HandwrittenListResponse(processing=processing, completed=completed)

    except Exception as e:
        logger.error(f"Error listing handwritten documents for group {group_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve handwritten documents.")


@router.get("/{task_id}/status", response_model=HandwrittenStatusResponse)
def get_handwritten_status(
    task_id: str = Path(..., description="The task ID of the handwritten document processing."),
    storage: HandwrittenDocumentStorage = Depends(get_handwritten_storage),
):
    """
    Get the processing status of a handwritten document.
    """
    logger.info(f"Checking status for handwritten document task {task_id}")

    try:
        # Get from storage first
        document = storage.get_document(task_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")

        # Check Celery task status
        task_result = AsyncResult(task_id, app=process_handwritten_document_task.app)

        # Update status if task is complete
        if task_result.ready():
            if task_result.successful():
                result = task_result.get()
                storage.update_document_status(task_id, result)
                # Refresh document data
                document = storage.get_document(task_id)
            elif task_result.failed():
                error_result = {"status": "FAILURE", "error_message": str(task_result.result) if task_result.result else "Unknown error"}
                storage.update_document_status(task_id, error_result)
                document = storage.get_document(task_id)

        return HandwrittenStatusResponse(
            task_id=document.task_id, status=document.status, original_filename=document.original_filename, processed_filename=document.processed_filename, error_message=document.error_message
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error checking status for task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to check document status.")


@router.get("/{task_id}/download")
def download_processed_document(
    task_id: str = Path(..., description="The task ID of the processed document."),
    group_id: str = Header(..., alias="X-Group-ID"),
    storage: HandwrittenDocumentStorage = Depends(get_handwritten_storage),
):
    """
    Download the processed LaTeX PDF document.
    """
    logger.info(f"Download request for processed document {task_id} from group {group_id}")

    try:
        document = storage.get_document(task_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")

        # Validate group membership
        if document.group_id != group_id:
            raise HTTPException(status_code=403, detail="Access denied. You can only download documents from your own group.")

        if document.status != "SUCCESS":
            raise HTTPException(status_code=400, detail=f"Document is not ready for download. Status: {document.status}")

        file_path = storage.get_file_path(task_id, "processed")
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Processed file not found.")

        return FileResponse(path=str(file_path), media_type="application/pdf", filename=document.processed_filename or f"processed_{document.original_filename}")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error downloading document {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to download document.")


@router.delete("/{task_id}", response_model=HandwrittenDeleteResponse)
def delete_handwritten_document(
    task_id: str = Path(..., description="The task ID of the document to delete."),
    storage: HandwrittenDocumentStorage = Depends(get_handwritten_storage),
):
    """
    Delete a handwritten document and all its associated files.
    """
    logger.info(f"Delete request for handwritten document {task_id}")

    try:
        document = storage.get_document(task_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")

        # Delete the document
        success = storage.delete_document(task_id)

        if success:
            return HandwrittenDeleteResponse(task_id=task_id, message="Document successfully deleted.")
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error deleting document {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete document.")
