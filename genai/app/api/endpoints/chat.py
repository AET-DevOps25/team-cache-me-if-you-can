import logging

from app.core.rag_pipeline import RAGSystem, get_rag_system_instance
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    DocumentMetadata,
    SourceDocument,
)
from fastapi import APIRouter, HTTPException, Depends, Body

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_document(
    query_request: QueryRequest = Body(...),
    rag_system: RAGSystem = Depends(get_rag_system_instance),
):
    """
    Endpoint to ask a question about the indexed documents.
    Uses the RAG pipeline to generate an answer.
    """
    if not query_request.question or not query_request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        logger.info(f"Received query: {query_request.question}")

        # The rag_system now returns a dictionary with the answer and source documents
        result = await rag_system.invoke_chain(query_request.question)

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
