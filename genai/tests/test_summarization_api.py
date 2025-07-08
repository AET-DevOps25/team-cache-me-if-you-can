import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.summarization_service import SummarizationService, get_summarization_service

# Mock SummarizationService
class MockSummarizationService:
    async def summarize_document(self, filename: str):
        if "non_existent.pdf" in filename:
            return "Could not find the document specified."
        if "error.pdf" in filename:
            return "An error occurred during summarization."
        return "This is a summary of the document."

async def get_mock_summarization_service():
    return MockSummarizationService()

@pytest.fixture
def summary_test_client():
    original_override = app.dependency_overrides.get(get_summarization_service)
    app.dependency_overrides[get_summarization_service] = get_mock_summarization_service
    yield TestClient(app)
    if original_override:
        app.dependency_overrides[get_summarization_service] = original_override
    else:
        del app.dependency_overrides[get_summarization_service]

def test_summarize_document_success(summary_test_client: TestClient):
    """
    Tests successful summarization of a document.
    """
    filename = "existing_document.pdf"
    response = summary_test_client.post(f"/api/v1/summaries/{filename}/summarize")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == filename
    assert data["summary"] == "This is a summary of the document."

def test_summarize_document_not_found(summary_test_client: TestClient):
    """
    Tests summarization when the document is not found.
    """
    filename = "non_existent.pdf"
    response = summary_test_client.post(f"/api/v1/summaries/{filename}/summarize")
    assert response.status_code == 404
    assert "Could not find the document" in response.json()["detail"]

def test_summarize_document_error(summary_test_client: TestClient):
    """
    Tests summarization when an error occurs.
    """
    filename = "error.pdf"
    response = summary_test_client.post(f"/api/v1/summaries/{filename}/summarize")
    assert response.status_code == 500
    assert "An error occurred" in response.json()["detail"] 