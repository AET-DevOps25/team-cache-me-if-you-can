import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.services.document_service import (
    DocumentProcessingService,
    get_document_processing_service,
)
from app.models.schemas import DocumentUploadResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
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
        logger.info(f"Received file for upload: {file.filename}")
        contents = await file.read()

        docs_indexed, error_message = await doc_service.process_and_index_document(contents, file.filename)

        if error_message:
            logger.error(f"Error processing {file.filename}: {error_message}")
            return DocumentUploadResponse(
                filename=file.filename,
                message="Failed to process document.",
                error=error_message,
            )

        logger.info(f"Successfully processed and initiated indexing for {file.filename}. Documents created: {docs_indexed}")
        return DocumentUploadResponse(
            filename=file.filename,
            message="Document processed and sent for indexing successfully.",
            document_count=docs_indexed,
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
