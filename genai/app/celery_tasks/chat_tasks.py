import asyncio
from app.core.rag_pipeline import RAGSystem
from app.celery_app import celery_app


@celery_app.task
def process_query_task(question: str, tenant: str) -> dict:
    """
    Celery task to process a query using the RAG system.
    """
    rag_system = RAGSystem()
    # Running the async invoke_chain in a synchronous Celery task
    result = asyncio.run(rag_system.invoke_chain(question, tenant=tenant))

    # Convert Document objects to dictionaries
    if "source_documents" in result and result["source_documents"] is not None:
        result["source_documents"] = [
            {
                "page_content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in result["source_documents"]
        ]

    return result
