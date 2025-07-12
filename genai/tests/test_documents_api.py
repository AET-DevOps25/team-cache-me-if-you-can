import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile, status
from unittest.mock import MagicMock, patch
from app.main import app
from app.services.document_service import (
    DocumentProcessingService,
    get_document_processing_service,
)
import app.services.document_service as doc_service_module
from app.models.schemas import DocumentUploadResponse
import io
from celery.result import AsyncResult

# Reset global states and overrides before defining tests for this module
app.dependency_overrides.clear()
doc_service_module._document_processing_service_instance = None


# Mock DocumentProcessingService
class MockDocumentProcessingService:
    async def process_and_index_document(self, contents: bytes, filename: str, tenant: str):
        # Simulate processing
        if "error" in filename:
            return 0, "Simulated processing error"
        if "success" in filename:
            return 3, None  # Simulate 3 documents indexed
        return 1, None  # Default simulation

    def get_all_documents(self, tenant: str):
        return ["doc1.pdf", "doc2.pdf"]

    async def delete_document(self, filename: str, tenant: str):
        if filename == "existing_doc.pdf":
            return True, f"Successfully deleted document '{filename}'."
        elif filename == "non_existing_doc.pdf":
            return False, f"Document '{filename}' not found."
        elif filename == "error_doc.pdf":
            raise Exception("DB error")
        return False, "Should not be reached"


async def get_mock_document_processing_service():
    return MockDocumentProcessingService()


@pytest.fixture
def doc_test_client():
    original_override = app.dependency_overrides.get(get_document_processing_service)
    original_singleton_instance = doc_service_module._document_processing_service_instance

    # Reset singleton and apply specific override
    doc_service_module._document_processing_service_instance = None
    app.dependency_overrides[get_document_processing_service] = get_mock_document_processing_service

    yield TestClient(app)

    # Teardown: Restore original state
    if original_override:
        app.dependency_overrides[get_document_processing_service] = original_override
    elif get_document_processing_service in app.dependency_overrides:
        del app.dependency_overrides[get_document_processing_service]
    doc_service_module._document_processing_service_instance = original_singleton_instance


# Update tests to use the client from the fixture
def test_upload_document_success_pdf(doc_test_client: TestClient, mocker):
    # Mock the Celery task
    mock_task = MagicMock()
    mock_task.id = "test-task-id-pdf"
    mocker.patch(
        "app.celery_tasks.document_tasks.process_and_index_document_task.delay",
        return_value=mock_task,
    )

    file_content = b"dummy pdf content"
    file_name = "success_test.pdf"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "application/pdf")},
        headers={"X-Group-ID": "test_group"},
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["filename"] == file_name
    assert data["message"] == "Document uploaded and processing started in background."
    assert "task_id" in data


def test_upload_document_success_docx(doc_test_client: TestClient, mocker):
    # Mock the Celery task
    mock_task = MagicMock()
    mock_task.id = "test-task-id-docx"
    mocker.patch(
        "app.celery_tasks.document_tasks.process_and_index_document_task.delay",
        return_value=mock_task,
    )

    file_content = b"dummy docx content"
    file_name = "success_test.docx"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                file_name,
                io.BytesIO(file_content),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        headers={"X-Group-ID": "test_group"},
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["filename"] == file_name
    assert data["message"] == "Document uploaded and processing started in background."
    assert "task_id" in data


def test_upload_document_success_pptx(doc_test_client: TestClient, mocker):
    # Mock the Celery task
    mock_task = MagicMock()
    mock_task.id = "test-task-id-pptx"
    mocker.patch(
        "app.celery_tasks.document_tasks.process_and_index_document_task.delay",
        return_value=mock_task,
    )

    file_content = b"dummy pptx content"
    file_name = "success_test.pptx"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                file_name,
                io.BytesIO(file_content),
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
        },
        headers={"X-Group-ID": "test_group"},
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["filename"] == file_name
    assert data["message"] == "Document uploaded and processing started in background."
    assert "task_id" in data


def test_upload_document_unsupported_type(doc_test_client: TestClient):
    file_content = b"dummy text content"
    file_name = "test.txt"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "text/plain")},
        headers={"X-Group-ID": "test_group"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported file type: 'txt'" in data["detail"]


def test_upload_document_no_extension(doc_test_client: TestClient):
    file_content = b"dummy content"
    file_name = "testfile"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "application/octet-stream")},
        headers={"X-Group-ID": "test_group"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "File has no extension." in data["detail"]


def test_upload_document_processing_error(doc_test_client: TestClient, mocker):
    mocker.patch(
        "app.celery_tasks.document_tasks.process_and_index_document_task.delay",
        side_effect=Exception("Celery error"),
    )
    file_content = b"dummy pdf content for error"
    file_name = "error_test.pdf"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "application/pdf")},
        headers={"X-Group-ID": "test_group"},
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert "An unexpected server error occurred." in data["message"]
    assert "error" in data


def test_delete_document_success(doc_test_client: TestClient):
    response = doc_test_client.delete("/api/v1/documents/existing_doc.pdf", headers={"X-Group-ID": "test_group"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["filename"] == "existing_doc.pdf"
    assert "Successfully deleted" in data["message"]


def test_delete_document_not_found(doc_test_client: TestClient):
    response = doc_test_client.delete("/api/v1/documents/non_existing_doc.pdf", headers={"X-Group-ID": "test_group"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "not found" in data["detail"]


def test_get_document_upload_status_success(doc_test_client: TestClient, mocker):
    mock_result = MagicMock(spec=AsyncResult)
    mock_result.status = "SUCCESS"
    mock_result.result = {"filename": "test.pdf", "docs_indexed": 5, "error_message": None}
    mock_result.failed.return_value = False

    with patch("app.api.endpoints.documents.AsyncResult", return_value=mock_result):
        response = doc_test_client.get("/api/v1/documents/upload/status/some-task-id")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == "some-task-id"
        assert data["status"] == "SUCCESS"
        assert data["result"]["docs_indexed"] == 5
        assert data["result"]["filename"] == "test.pdf"


def test_get_document_upload_status_failed(doc_test_client: TestClient, mocker):
    mock_result = MagicMock(spec=AsyncResult)
    mock_result.status = "FAILURE"
    mock_result.result = "Processing failed horribly"
    mock_result.failed.return_value = True
    mock_result.traceback = "Traceback..."

    with patch("app.api.endpoints.documents.AsyncResult", return_value=mock_result):
        response = doc_test_client.get("/api/v1/documents/upload/status/failed-task-id")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "FAILURE"
        assert "Processing failed horribly" in data["result"]["error_message"]


# Clean up dependency overrides if necessary
def teardown_module(module):
    app.dependency_overrides.clear()
