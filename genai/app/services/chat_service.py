# app/core/chat_service.py
import logging
import asyncio
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from app.core.rag_pipeline import RAGSystem, get_rag_system_instance
from app.core.llm import get_llm_instance
from app.vector_store.weaviate_connector import get_retriever
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class ChatResponseSource(BaseModel):
    document_id: str = Field(
        description="Unique identifier for the source document (e.g., from metadata)."
    )
    source_name: str = Field(
        description="Display name of the source (e.g., filename, lecture title)."
    )
    page_number: Optional[int] = Field(
        None, description="Page number within the document, if applicable."
    )
    content_snippet: Optional[str] = Field(
        None, description="A small snippet of the relevant content."
    )


class ChatResponse(BaseModel):
    answer: str = Field(description="The AI-generated answer to the query.")
    sources: List[ChatResponseSource] = Field(
        default_factory=list, description="List of sources used to generate the answer."
    )
    # session_id: Optional[str] = None # If you track chat sessions


class ChatService:
    def __init__(self, rag_system_instance: Optional[RAGSystem] = None):
        """
        Initializes the ChatService.
        Args:
            rag_system_instance: An optional pre-initialized RAGSystem instance.
                                 If None, it will try to get one using get_rag_system_instance().
        """
        try:
            self.rag_system: RAGSystem = (
                rag_system_instance or get_rag_system_instance()
            )
            logger.info("ChatService initialized successfully with RAG system.")
        except RuntimeError as e:
            logger.error(f"Failed to initialize RAGSystem in ChatService: {e}")
            # This service is unusable without RAG. Re-raise or handle appropriately.
            raise RuntimeError(
                f"ChatService could not be initialized: RAG system unavailable. {e}"
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during ChatService initialization: {e}",
                exc_info=True,
            )
            raise

    async def process_chat_query(
        self,
        query_text: str,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> ChatResponse:
        """
        Processes a chat query using the RAG system.
        Args:
            query_text: The text of the user's query.
            user_id: Optional ID of the user (for logging or future use).
            group_id: Optional ID of the study group for context filtering in retriever.

        Returns:
            A ChatResponse Pydantic model.
        """
        logger.info(
            f"Processing chat query: '{query_text}' for user '{user_id}', group '{group_id}'"
        )

        if not self.rag_system:
            # This check is somewhat redundant due to __init__ raising error, but good for safety.
            logger.error(
                "RAG system is not available in ChatService. This should not happen if initialization was successful."
            )
            raise RuntimeError("RAG system not available. Cannot process chat query.")

        try:

            answer_text = await self.rag_system.invoke_chain(query_text)

            source_documents: List[Document] = []
            if self.rag_system.retriever:
                retriever_kwargs: Dict[str, Any] = {}
                if group_id:

                    retriever_kwargs["metadata"] = {"group_id": group_id}
                    logger.debug(
                        f"Attempting to retrieve documents with filter for group_id: {group_id}"
                    )

                source_documents = (
                    await self.rag_system.retriever.aget_relevant_documents(
                        query_text, **retriever_kwargs
                    )
                )
                logger.debug(
                    f"Retrieved {len(source_documents)} source documents for query '{query_text}'."
                )

            # 3. Format sources for the response
            retrieved_sources_formatted: List[ChatResponseSource] = []
            for doc in source_documents:
                # Assuming 'source_filename', 'doc_id', 'page_number' are in doc.metadata
                # Adjust these keys based on your actual document metadata structure
                retrieved_sources_formatted.append(
                    ChatResponseSource(
                        document_id=str(
                            doc.metadata.get(
                                "doc_id", doc.metadata.get("id", "unknown")
                            )
                        ),
                        source_name=str(
                            doc.metadata.get(
                                "source", doc.metadata.get("filename", "Unknown Source")
                            )
                        ),
                        page_number=doc.metadata.get("page_number", None),
                        content_snippet=(
                            doc.page_content[:200] + "..." if doc.page_content else ""
                        ),  # Example snippet
                    )
                )

            response = ChatResponse(
                answer=answer_text, sources=retrieved_sources_formatted
            )
            logger.info(
                f"Generated ChatResponse for query '{query_text}'. Answer: '{answer_text[:100]}...'"
            )
            return response

        except Exception as e:
            logger.error(
                f"Error processing chat query '{query_text}': {e}", exc_info=True
            )
            # Depending on API design, you might return a specific error response model
            # or re-raise a custom exception. For now, re-raising.
            raise


# --- Optional: Global instance or dependency injection setup ---
# chat_service_instance: Optional[ChatService] = None


def get_chat_service_instance() -> ChatService:
    global chat_service_instance
    if chat_service_instance is None:
        # This ensures that RAG system (and its dependencies like LLM) are initialized first
        try:
            # RAGSystem's constructor will call get_llm_instance and get_retriever
            rag_sys = get_rag_system_instance()  # Ensures RAG is ready
            chat_service_instance = ChatService(rag_system_instance=rag_sys)
        except Exception as e:
            logger.fatal(
                f"CRITICAL: Failed to initialize ChatService instance: {e}",
                exc_info=True,
            )
            raise RuntimeError(f"Could not create ChatService: {e}")
    return chat_service_instance


# --- Example Usage for standalone testing ---
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv, find_dotenv
    from unittest.mock import patch, AsyncMock  # For mocking async methods
    from langchain_core.retrievers import BaseRetriever

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Running chat_service.py standalone test...")

    env_path = find_dotenv()
    if env_path:
        logger.info(f"Loading .env file from: {env_path}")
        load_dotenv(dotenv_path=env_path)
        from app.config import Settings, settings as app_settings

        settings_instance = Settings()
        app_settings.OPENAI_API_KEY = (
            os.getenv("OPENAI_API_KEY") or app_settings.OPENAI_API_KEY
        )
        app_settings.OPENAI_MODEL_NAME = (
            os.getenv("OPENAI_MODEL_NAME") or app_settings.OPENAI_MODEL_NAME
        )
    else:
        logger.warning(
            "No .env file found. Relying on environment variables or defaults for OPENAI_API_KEY."
        )

    class MockChatServiceRetriever(BaseRetriever):
        def _get_relevant_documents(
            self, query: str, *, run_manager=None, **kwargs
        ) -> List[Document]:
            logger.info(
                f"[MockChatServiceRetriever SYNC] Getting documents for: {query}, kwargs: {kwargs}"
            )
            docs = []
            if "python" in query.lower():
                docs.append(
                    Document(
                        page_content="Python is a versatile programming language.",
                        metadata={
                            "doc_id": "py001",
                            "source": "python_intro.pdf",
                            "page_number": 1,
                        },
                    )
                )
            if " AVL tree" in query.lower():  # From rag_pipeline test
                docs.append(
                    Document(
                        page_content="AVL trees use rotations.",
                        metadata={"doc_id": "avl002", "source": "datastructures.txt"},
                    )
                )

            if (
                kwargs.get("metadata")
                and kwargs["metadata"].get("group_id") == "group123"
            ):
                docs.append(
                    Document(
                        page_content="This document is specific to group123.",
                        metadata={"doc_id": "grp001", "source": "group_doc.pdf"},
                    )
                )
            elif kwargs.get("metadata") and kwargs["metadata"].get("group_id"):
                pass  # for simplicity, current docs remain
            return docs

        async def _aget_relevant_documents(
            self, query: str, *, run_manager=None, **kwargs
        ) -> List[Document]:
            logger.info(
                f"[MockChatServiceRetriever ASYNC] Getting documents for: {query}, kwargs: {kwargs}"
            )
            await asyncio.sleep(0.05)  # Simulate async
            return self._get_relevant_documents(
                query, run_manager=run_manager, **kwargs
            )

    async def main_chat_test():
        logger.info("--- Starting ChatService Test ---")

        mock_retriever_instance = MockChatServiceRetriever()

        with patch(
            "app.core.rag_pipeline.get_retriever", return_value=mock_retriever_instance
        ) as mock_get_retriever_func:

            try:
                rag_system_for_test = RAGSystem()

            except Exception as e:
                logger.error(
                    f"Failed to initialize RAGSystem for ChatService test: {e}. Check OPENAI_API_KEY and imports."
                )
                logger.error(
                    "If OPENAI_API_KEY is missing, LLMProvider in llm.py or EmbeddingProvider in embeddings.py will raise ValueError."
                )
                return

            try:
                chat_svc = ChatService(rag_system_instance=rag_system_for_test)

                test_query_1 = "Tell me about Python programming."
                logger.info(f'\n[Test 1] Query: "{test_query_1}"')
                response_1 = await chat_svc.process_chat_query(
                    test_query_1, user_id="test_user_01"
                )
                logger.info(f"ChatService Response 1 Answer: {response_1.answer}")
                logger.info(f"ChatService Response 1 Sources: {response_1.sources}")
                assert (
                    "Python" in response_1.answer or "versatile" in response_1.answer
                )  # depends on LLM
                assert any("py001" in s.document_id for s in response_1.sources)

                test_query_2 = "What are AVL tree rotations?"
                logger.info(f'\n[Test 2] Query: "{test_query_2}" with group_id')
                response_2 = await chat_svc.process_chat_query(
                    test_query_2, user_id="test_user_02", group_id="group123"
                )
                logger.info(f"ChatService Response 2 Answer: {response_2.answer}")
                logger.info(f"ChatService Response 2 Sources: {response_2.sources}")
                assert "AVL" in response_2.answer or "rotations" in response_2.answer
                assert any("avl002" in s.document_id for s in response_2.sources)
                # Check if group-specific document was retrieved due to group_id
                assert any(
                    "grp001" in s.document_id for s in response_2.sources
                ), "Group-specific document not found"

                test_query_3 = "What is the weather today?"
                logger.info(
                    f'\n[Test 3] Query: "{test_query_3}" (no specific context in mock)'
                )
                response_3 = await chat_svc.process_chat_query(
                    test_query_3, user_id="test_user_03"
                )
                logger.info(f"ChatService Response 3 Answer: {response_3.answer}")
                logger.info(f"ChatService Response 3 Sources: {response_3.sources}")
                assert len(response_3.sources) == 0 or not any(
                    s.document_id
                    for s in response_3.sources
                    if s.document_id not in ["unknown"]
                )

            except RuntimeError as e:
                logger.error(f"Runtime error during ChatService operation: {e}")
            except Exception as e:
                logger.error(f"Error during ChatService test: {e}", exc_info=True)

    if (
        __name__ == "__main__"
    ):  # Ensure this check again for clarity if script is run directly
        try:
            asyncio.run(main_chat_test())
        except Exception as e:
            logger.error(f"Fatal error running main_chat_test: {e}", exc_info=True)
