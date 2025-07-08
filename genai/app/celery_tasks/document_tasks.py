from app.celery_app import celery_app
from app.services.document_processor import process_pdf_to_latex_pdf


@celery_app.task
def process_document_task(pdf_path: str):
    """
    Celery task to process a PDF file.
    """
    return process_pdf_to_latex_pdf(pdf_path)
