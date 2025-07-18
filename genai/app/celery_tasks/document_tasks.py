from app.celery_app import celery_app
from app.services.document_processor import process_pdf_to_latex_pdf
import asyncio
from app.services.document_service import DocumentProcessingService
from typing import Dict
import logging
from pathlib import Path
import tempfile
import os
from datetime import datetime

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


@celery_app.task
def process_handwritten_document_task(file_content: bytes, filename: str, group_id: str, task_id: str = None) -> Dict:
    """
    Celery task to process a handwritten PDF document, converting it to LaTeX PDF.

    Args:
        file_content: The PDF file content as bytes
        filename: Original filename
        group_id: Group ID for organization
        task_id: Task ID for tracking (if None, will use Celery task ID)

    Returns:
        Dict with processing results including file paths and metadata
    """
    # Use Celery task ID if no custom task_id provided
    if task_id is None:
        task_id = process_handwritten_document_task.request.id

    logger.info(f"Starting handwritten document processing for {filename} in group {group_id}, task {task_id}")

    # Create directories for handwritten documents
    handwritten_dir = Path("app/data/handwritten")
    handwritten_dir.mkdir(parents=True, exist_ok=True)

    group_dir = handwritten_dir / group_id
    group_dir.mkdir(parents=True, exist_ok=True)

    task_dir = group_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Save the original PDF file
        original_pdf_path = task_dir / f"original_{filename}"
        with open(original_pdf_path, "wb") as f:
            f.write(file_content)

        logger.info(f"Saved original PDF to {original_pdf_path}")

        # Process the PDF to LaTeX PDF
        processed_pdf_path = process_pdf_to_latex_pdf(str(original_pdf_path))

        if processed_pdf_path and Path(processed_pdf_path).exists():
            # Move the processed file to our managed directory
            processed_filename = f"processed_{Path(filename).stem}.pdf"
            final_processed_path = task_dir / processed_filename

            # Move the file to our managed location
            import shutil

            shutil.move(processed_pdf_path, final_processed_path)

            # Clean up any temporary LaTeX files
            tex_file = Path(str(original_pdf_path).replace(".pdf", ".tex"))
            if tex_file.exists():
                tex_file.unlink()

            # Clean up any other LaTeX compilation artifacts
            for ext in [".aux", ".log", ".fls", ".fdb_latexmk"]:
                artifact_file = Path(str(original_pdf_path).replace(".pdf", ext))
                if artifact_file.exists():
                    artifact_file.unlink()

            logger.info(f"Successfully processed {filename} to {final_processed_path}")

            return {
                "task_id": task_id,
                "group_id": group_id,
                "original_filename": filename,
                "processed_filename": processed_filename,
                "original_path": str(original_pdf_path),
                "processed_path": str(final_processed_path),
                "status": "SUCCESS",
                "timestamp": datetime.now().isoformat(),
                "error_message": None,
            }
        else:
            logger.error(f"Failed to process {filename} - no output file generated")
            return {
                "task_id": task_id,
                "group_id": group_id,
                "original_filename": filename,
                "processed_filename": None,
                "original_path": str(original_pdf_path),
                "processed_path": None,
                "status": "FAILURE",
                "timestamp": datetime.now().isoformat(),
                "error_message": "Failed to generate processed PDF",
            }

    except Exception as e:
        logger.error(f"Error processing handwritten document {filename}: {e}", exc_info=True)
        return {
            "task_id": task_id,
            "group_id": group_id,
            "original_filename": filename,
            "processed_filename": None,
            "original_path": None,
            "processed_path": None,
            "status": "FAILURE",
            "timestamp": datetime.now().isoformat(),
            "error_message": str(e),
        }
