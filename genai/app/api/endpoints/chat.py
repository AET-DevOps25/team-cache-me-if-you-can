import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from app.core.rag_pipeline import (
    RAGSystem,
    get_rag_system_instance,
)  # RAGSystem uses the updated retriever
from app.models.schemas import QueryRequest, QueryResponse

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
        # The RAG system's invoke_chain is async
        answer = await rag_system.invoke_chain(query_request.question)

        # Note: The current RAG chain returns only the answer string.
        # To include source documents, the RAG chain itself would need to be modified
        # to return them alongside the answer, or we perform a separate
        # retrieval step.

        # For now, we'll simulate fetching source documents if needed for the response.
        # A more robust way is to modify RAGSystem to return context.
        retrieved_docs = []
        if hasattr(rag_system.rag_chain.steps[0], "invoke") and hasattr(rag_system.retriever, "get_relevant_documents"):
            # This is a simplified way; ideally, context is part of RAG chain output
            # The RunnableParallel now has a retriever associated with the 'context' key.
            # We need to access the retrieved documents that were fed into the prompt.
            # This part is tricky as LCEL chains don't easily expose intermediate step outputs by default.
            # One way is to run the retriever separately, or modify the chain
            # to output context.

            # For simplicity, let's assume the RAG chain can be modified or we re-retrieve for sources.
            # This is NOT ideal as it duplicates retrieval if RAG already did it.
            # A better RAG chain would be: (context_and_question | prompt | llm | parser)
            # where context_and_question = RunnableParallel(question=Passthrough(), context=retriever)
            # then the output of context_and_question could be passed along.

            # Let's try to get docs from the retriever directly for the response (might differ slightly from RAG context)
            # This is just for the API response, RAG used its own internal retrieval.
            # context_docs_for_response =
            # rag_system.retriever.get_relevant_documents(query_request.question)
            # # sync
            context_docs_for_response = await rag_system.retriever.aget_relevant_documents(query_request.question)  # async

            for doc in context_docs_for_response:
                source_info = {
                    "page_content": (doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content),
                    "metadata": doc.metadata,
                }
                retrieved_docs.append(source_info)

        logger.info(f"Generated answer for query '{query_request.question}': {answer}")
        return QueryResponse(answer=answer, source_documents=retrieved_docs)

    except Exception as e:
        logger.error(f"Error processing query '{query_request.question}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {str(e)}",
        )
