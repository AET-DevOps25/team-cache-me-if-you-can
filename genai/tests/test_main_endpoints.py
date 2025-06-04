import pytest
from fastapi.testclient import TestClient
from app.main import app  # Assuming 'app' is the root of the project for imports
from app.config import settings

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": f"Welcome to {settings.APP_NAME}! Navigate to /docs for API documentation."}


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"} 