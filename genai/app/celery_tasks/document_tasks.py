from app.celery_app import celery_app
from app.services.document_processor import process_pdf_to_latex_pdf
import asyncio
from app.services.document_service import DocumentProcessingService
from typing import Dict
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def process_document_task(pdf_path: str):
    """
    Celery task to process a PDF file.
    """
    return process_pdf_to_latex_pdf(pdf_path)


@celery_app.task
def process_and_index_document_task(file_content: bytes, filename: str, tenant: str) -> Dict:
    """
    Celery task to process and index a document asynchronously.
    """
    service = DocumentProcessingService()
    docs_indexed, error_message = asyncio.run(service.process_and_index_document(file_content, filename, tenant))
    return {"filename": filename, "docs_indexed": docs_indexed, "error_message": error_message}
