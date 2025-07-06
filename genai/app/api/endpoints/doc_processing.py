import os
import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from celery.result import AsyncResult
from app.celery_worker import process_document_task

router = APIRouter()

# Directory to store uploaded and generated files
FILES_DIR = Path("app/data/processed")
FILES_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload-and-process/")
async def upload_and_process_document(file: UploadFile = File(...)):
    """
    Upload a PDF, start the processing task, and return a task ID.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted.")

    try:
        # Save the uploaded file
        file_path = FILES_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Start the Celery task
        task = process_document_task.delay(str(file_path))

        return {"task_id": task.id}
    finally:
        file.file.close()


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """
    Get the status of a Celery task.
    """
    task_result = AsyncResult(task_id, app=process_document_task.app)
    status = task_result.status
    result = task_result.result if task_result.ready() else None

    if status == 'FAILURE':
        # If the task failed, return the error message
        return {"status": status, "error": str(result)}
    
    return {"status": status, "result": result}


@router.get("/files/{file_name}")
async def get_file(file_name: str):
    """
    Download a generated file.
    """
    file_path = FILES_DIR / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=file_path, media_type='application/pdf', filename=file_name) 