import os
from celery import Celery
from app.services.document_processor import process_pdf_to_latex_pdf
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery("tasks", broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"), backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"))


@celery_app.task
def process_document_task(pdf_path: str):
    """
    Celery task to process a PDF file.
    """
    return process_pdf_to_latex_pdf(pdf_path)
