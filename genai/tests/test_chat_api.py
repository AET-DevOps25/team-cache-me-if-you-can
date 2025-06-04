import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.rag_pipeline import RAGSystem, get_rag_system_instance
import app.core.rag_pipeline as rag_module  # Import the module
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    DocumentMetadata,
    SourceDocument,
)


# Mock RAGSystem
class MockRetriever:
    async def aget_relevant_documents(self, query: str):
        # Simulate document retrieval
        if "no_docs_query" in query:
            return []
        return [
            SourceDocument(
                page_content="Mocked relevant document content.",
                metadata=DocumentMetadata(source="mock_source.pdf", page_number=1),
            ),
            SourceDocument(
                page_content="Another mocked relevant document.",
                metadata=DocumentMetadata(source="mock_source_2.pdf"),
            ),
        ]


class MockRAGSystem:
    def __init__(self):
        self.retriever = MockRetriever()

        # Simplified mock for rag_chain and its steps for the purpose of testing the endpoint
        # In a real scenario, this mock might need to be more sophisticated
        # depending on how rag_chain.steps[0] is used in the endpoint.
        # For the current endpoint code, steps[0] needs an invoke attribute if it exists.
        # However, the endpoint logic checks `hasattr(rag_system.rag_chain.steps[0], "invoke")`
        # which means rag_chain or rag_chain.steps might not exist or steps[0] might not have invoke.
        # We'll simulate a case where it exists and has an invoke for completeness.
        class MockStep:
            async def invoke(self, *args, **kwargs):
                return "Some result from a step"

        class MockChain:
            def __init__(self):
                self.steps = [MockStep()]

        self.rag_chain = MockChain()

    async def invoke_chain(self, query: str):
        if "error_query" in query:
            raise ValueError("Simulated RAG system error")
        return "This is a mocked answer to your question: " + query


async def get_mock_rag_system_instance():
    return MockRAGSystem()


@pytest.fixture
def chat_test_client():
    original_override = app.dependency_overrides.get(get_rag_system_instance)
    original_singleton_instance = rag_module.rag_system_instance

    # Reset singleton and apply specific override
    rag_module.rag_system_instance = None
    app.dependency_overrides[get_rag_system_instance] = get_mock_rag_system_instance

    yield TestClient(app)

    # Teardown: Restore original state
    if original_override:
        app.dependency_overrides[get_rag_system_instance] = original_override
    elif get_rag_system_instance in app.dependency_overrides:
        del app.dependency_overrides[get_rag_system_instance]
    rag_module.rag_system_instance = original_singleton_instance


# Update tests to use the client from the fixture
def test_query_document_success(chat_test_client: TestClient):
    query = "What is the capital of France?"
    response = chat_test_client.post("/api/v1/chat/query", json={"question": query})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mocked answer to your question: " + query
    assert len(data["source_documents"]) == 2
    assert data["source_documents"][0]["page_content"] == "Mocked relevant document content."
    assert data["source_documents"][0]["metadata"]["source"] == "mock_source.pdf"


def test_query_document_no_docs_retrieved(chat_test_client: TestClient):
    query = "no_docs_query specific phrase"
    response = chat_test_client.post("/api/v1/chat/query", json={"question": query})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mocked answer to your question: " + query
    assert len(data["source_documents"]) == 0


def test_query_document_empty_question(chat_test_client: TestClient):
    response = chat_test_client.post("/api/v1/chat/query", json={"question": "   "})  # Empty or whitespace only
    assert response.status_code == 400
    data = response.json()
    assert "Question cannot be empty." in data["detail"]


def test_query_document_no_question_field(chat_test_client: TestClient):
    response = chat_test_client.post("/api/v1/chat/query", json={})  # Missing question field
    # FastAPI should return 422 for validation error
    assert response.status_code == 422


def test_query_document_rag_system_error(chat_test_client: TestClient):
    query = "error_query induce system failure"
    response = chat_test_client.post("/api/v1/chat/query", json={"question": query})
    assert response.status_code == 500
    data = response.json()
    assert "An error occurred while processing your question: Simulated RAG system error" in data["detail"]


# Remove old module-level client and teardown_module if they exist
# (No explicit teardown_module was in the previous version of this specific file from snippets)
# The global `client = TestClient(app)` and `app.dependency_overrides[...] = ...` at module level are removed implicitly by this new structure.
