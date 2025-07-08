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

        # Simulate document retrieval to match the expected dictionary output
        source_documents = await self.retriever.aget_relevant_documents(query)

        return {
            "answer": "This is a mocked answer to your question: " + query,
            "source_documents": source_documents,
        }


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
    """
    Tests a successful query to the RAG pipeline.
    """
    query = "What is the capital of France?"
    response = chat_test_client.post("/api/v1/chat/query/sync", json={"question": query})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mocked answer to your question: " + query
    assert len(data["source_documents"]) == 2
    assert data["source_documents"][0]["page_content"] == "Mocked relevant document content."
    assert data["source_documents"][0]["metadata"]["source"] == "mock_source.pdf"


def test_query_document_no_docs_retrieved(chat_test_client: TestClient, mocker):
    """
    Tests the scenario where the RAG pipeline retrieves no documents.
    """
    query = "no_docs_query specific phrase"
    mocker.patch(
        "app.core.rag_pipeline.RAGSystem.invoke_chain",
        return_value={"answer": "I don't know.", "source_documents": []},
    )
    response = chat_test_client.post("/api/v1/chat/query/sync", json={"question": query})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data


def test_query_document_empty_question(chat_test_client: TestClient):
    """
    Tests the behavior with an empty question.
    """
    response = chat_test_client.post(
        "/api/v1/chat/query/sync", json={"question": "   "}
    )  # Empty or whitespace only
    assert response.status_code == 400


def test_query_document_no_question_field(chat_test_client: TestClient):
    """
    Tests the behavior when the question field is missing.
    """
    response = chat_test_client.post(
        "/api/v1/chat/query/sync", json={}
    )  # Missing question field
    # FastAPI should return 422 for validation error
    assert response.status_code == 422


def test_query_document_rag_system_error(chat_test_client: TestClient, mocker):
    """
    Tests the behavior when the RAG pipeline raises an exception.
    """
    query = "error_query induce system failure"
    mocker.patch(
        "app.core.rag_pipeline.RAGSystem.invoke_chain",
        side_effect=Exception("RAG system failure"),
    )
    response = chat_test_client.post("/api/v1/chat/query/sync", json={"question": query})
    assert response.status_code == 500


def test_query_document_async_starts_task(chat_test_client: TestClient, mocker):
    """
    Tests that the async query endpoint starts a task and returns a task ID.
    """
    mock_task = mocker.patch("app.api.endpoints.chat.process_query_task.delay")
    mock_task.return_value = mocker.MagicMock(id="test_task_id")

    query = "What is the meaning of life, asynchronously?"
    response = chat_test_client.post("/api/v1/chat/query/async", json={"question": query})

    assert response.status_code == 202
    data = response.json()
    assert data["task_id"] == "test_task_id"
    mock_task.assert_called_once_with(query)


def test_get_query_result_pending(chat_test_client: TestClient, mocker):
    """
    Tests checking the result of a pending task.
    """
    mock_async_result = mocker.patch("app.api.endpoints.chat.AsyncResult")
    mock_async_result.return_value.ready.return_value = False
    mock_async_result.return_value.status = "PENDING"

    task_id = "pending_task_id"
    response = chat_test_client.get(f"/api/v1/chat/query/result/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["status"] == "PENDING"
    assert data["result"] is None


def test_get_query_result_success(chat_test_client: TestClient, mocker):
    """
    Tests checking the result of a successful task.
    """
    mock_async_result = mocker.patch("app.api.endpoints.chat.AsyncResult")
    mock_async_result.return_value.ready.return_value = True
    mock_async_result.return_value.successful.return_value = True
    mock_async_result.return_value.status = "SUCCESS"
    mock_result = {
        "answer": "The task is complete.",
        "source_documents": [
            {"page_content": "doc1", "metadata": {"source": "s1", "page_number": 1}}
        ],
    }
    mock_async_result.return_value.get.return_value = mock_result

    task_id = "successful_task_id"
    response = chat_test_client.get(f"/api/v1/chat/query/result/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["status"] == "SUCCESS"
    assert data["result"]["answer"] == "The task is complete."
    assert len(data["result"]["source_documents"]) == 1

# Remove old module-level client and teardown_module if they exist
# (No explicit teardown_module was in the previous version of this specific file from snippets)
# The global `client = TestClient(app)` and `app.dependency_overrides[...] = ...` at module level are removed implicitly by this new structure.
