import logging
from celery.result import AsyncResult
from app.celery_tasks.chat_tasks import process_query_task

from app.core.rag_pipeline import RAGSystem, get_rag_system_instance
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    DocumentMetadata,
    SourceDocument,
    QueryTaskResponse,
    TaskStatusResponse,
)
from fastapi import APIRouter, HTTPException, Depends, Body, status, Header

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query/sync", response_model=QueryResponse)
async def query_document_sync(
    query_request: QueryRequest = Body(...),
    group_id: str = Header(..., alias="X-Group-ID"),
    rag_system: RAGSystem = Depends(get_rag_system_instance),
):
    """
    Endpoint to ask a question about the indexed documents.
    Uses the RAG pipeline to generate an answer.
    """
    if not query_request.question or not query_request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        logger.info(f"Received query: {query_request.question} for group {group_id}")

        # The rag_system now returns a dictionary with the answer and source documents
        result = await rag_system.invoke_chain(query_request.question, tenant=group_id)

        answer = result.get("answer", "An error occurred while generating the answer.")
        context_docs = result.get("source_documents", [])

        retrieved_docs_for_response = []
        for doc in context_docs:
            metadata_dict = doc.metadata if isinstance(doc.metadata, dict) else (doc.metadata.model_dump() if hasattr(doc.metadata, "model_dump") else {})

            source_doc = SourceDocument(
                page_content=(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content),
                metadata=DocumentMetadata(
                    source=metadata_dict.get("source", "Unknown source"),
                    page_number=metadata_dict.get("page_number"),
                ),
            )
            retrieved_docs_for_response.append(source_doc)

        logger.info(f"Generated answer for query '{query_request.question}': {answer}")
        return QueryResponse(answer=answer, source_documents=retrieved_docs_for_response)

    except Exception as e:
        logger.error(f"Error processing query '{query_request.question}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {str(e)}",
        )


@router.post("/query/async", response_model=QueryTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def query_document_async(
    query_request: QueryRequest = Body(...),
    group_id: str = Header(..., alias="X-Group-ID"),
):
    """
    Endpoint to ask a question about the indexed documents asynchronously.
    This will start a background task and return a task ID.
    """
    if not query_request.question or not query_request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        logger.info(f"Received async query: {query_request.question} for group {group_id}")
        task = process_query_task.delay(query_request.question, group_id)
        return QueryTaskResponse(task_id=task.id)

    except Exception as e:
        logger.error(f"Error starting async query '{query_request.question}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while starting the query task: {str(e)}",
        )


@router.get("/query/result/{task_id}", response_model=TaskStatusResponse)
async def get_query_result(task_id: str):
    """
    Endpoint to check the status of a query task and get the result.
    """
    task_result = AsyncResult(task_id)

    if task_result.ready():
        if task_result.successful():
            result = task_result.get()
            answer = result.get("answer", "An error occurred while generating the answer.")
            context_docs = result.get("source_documents", [])

            retrieved_docs_for_response = []
            for doc_data in context_docs:
                # The document from celery might be a dict, so we reconstruct the Pydantic model
                metadata_dict = doc_data.get("metadata", {})
                source_doc = SourceDocument(
                    page_content=doc_data.get("page_content"),
                    metadata=DocumentMetadata(
                        source=metadata_dict.get("source", "Unknown source"),
                        page_number=metadata_dict.get("page_number"),
                    ),
                )
                retrieved_docs_for_response.append(source_doc)

            query_response = QueryResponse(answer=answer, source_documents=retrieved_docs_for_response)
            return TaskStatusResponse(task_id=task_id, status=task_result.status, result=query_response)
        else:
            # Task failed
            return TaskStatusResponse(task_id=task_id, status="FAILED", result=None)
    else:
        # Task is still pending
        return TaskStatusResponse(task_id=task_id, status="PENDING", result=None)
