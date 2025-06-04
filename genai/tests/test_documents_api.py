import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile
from app.main import app
from app.services.document_service import DocumentProcessingService, get_document_processing_service
import app.services.document_service as doc_service_module
from app.models.schemas import DocumentUploadResponse
import io

# Reset global states and overrides before defining tests for this module
app.dependency_overrides.clear()
doc_service_module._document_processing_service_instance = None

# Mock DocumentProcessingService
class MockDocumentProcessingService:
    async def process_and_index_document(self, contents: bytes, filename: str):
        # Simulate processing
        if "error" in filename:
            return 0, "Simulated processing error"
        if "success" in filename:
            return 3, None  # Simulate 3 documents indexed
        return 1, None # Default simulation

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
def test_upload_document_success_pdf(doc_test_client: TestClient):
    file_content = b"dummy pdf content"
    file_name = "success_test.pdf"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == file_name
    assert data["message"] == "Document processed and sent for indexing successfully."
    assert data["document_count"] == 3
    assert data["error"] is None

def test_upload_document_success_docx(doc_test_client: TestClient):
    file_content = b"dummy docx content"
    file_name = "success_test.docx"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == file_name
    assert data["message"] == "Document processed and sent for indexing successfully."
    assert data["document_count"] == 3
    assert data["error"] is None

def test_upload_document_success_pptx(doc_test_client: TestClient):
    file_content = b"dummy pptx content"
    file_name = "success_test.pptx"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.presentationml.presentation")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == file_name
    assert data["message"] == "Document processed and sent for indexing successfully."
    assert data["document_count"] == 3
    assert data["error"] is None

def test_upload_document_unsupported_type(doc_test_client: TestClient):
    file_content = b"dummy text content"
    file_name = "test.txt"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "text/plain")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported file type: 'txt'" in data["detail"]

def test_upload_document_no_extension(doc_test_client: TestClient):
    file_content = b"dummy content"
    file_name = "testfile"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "application/octet-stream")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "File has no extension." in data["detail"]

def test_upload_document_processing_error(doc_test_client: TestClient):
    file_content = b"dummy pdf content for error"
    file_name = "error_test.pdf"
    response = doc_test_client.post(
        "/api/v1/documents/upload",
        files={"file": (file_name, io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == file_name
    assert data["message"] == "Failed to process document."
    assert data["error"] == "Simulated processing error"
    assert data.get("document_count") is None or data.get("document_count") == 0

# Removed old module-level client, singleton resets at top of file, and teardown_module

# To ensure app.dependency_overrides is cleaned up after tests in this file.
# However, TestClient creates a new app instance per test or uses a context manager usually.
# For simplicity here, we'll rely on the TestClient's behavior or assume pytest test isolation if needed.
# A more robust way would be to use pytest fixtures to manage dependency overrides.
# For now, this should work for sequential execution.
# If tests from other files are affected, we'll need a fixture-based approach for setup/teardown of overrides.

# Clean up dependency overrides if necessary (though TestClient usually handles this scope)
# This is more of a note: for robust parallel testing or complex scenarios, use fixtures.
# For now, we'll add a manual clear for illustration, but pytest fixtures are better.
def teardown_module(module):
    app.dependency_overrides.clear() 