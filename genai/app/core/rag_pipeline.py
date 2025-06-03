import asyncio
import logging
from typing import List

from app.core.llm import get_llm_instance
from app.vector_store.weaviate_connector import get_retriever
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Implements a Retrieval Augmented Generation (RAG) system.
    Combines a retriever, a prompt template, and an LLM to answer questions.
    """

    def __init__(self, llm: BaseChatModel = None, retriever: BaseRetriever = None):
        self.llm = llm or get_llm_instance()
        self.retriever = retriever or get_retriever()

        # Define a prompt template
        template = """
        You are an AI assistant for the StudySync platform. Your goal is to help students understand their course material.
        Answer the question using ONLY the provided context.
        If the context contains direct information or relevant examples that help answer the question, synthesize a concise answer.
        If the context does not contain relevant information to answer the question, clearly state that you don't know.
        Do not make up information or provide knowledge beyond the provided context.

        Context:
        {context}

        Question: {question}

        Answer:
        """
        self.prompt = ChatPromptTemplate.from_template(template)

        # Define the RAG chain using LangChain Expression Language (LCEL)
        # The context is formatted by the retriever's format_docs function (default simple join).
        # RunnableParallel allows "context" and "question" to be processed
        # (retrieved/passed) in parallel.
        self.rag_chain = (
            RunnableParallel(
                context=(lambda x: x["question"]) | self.retriever,
                # Pass question to retriever for context
                question=RunnablePassthrough(),  # Pass original question through
            )  # Alternative if retriever needs the full input dict:
            # {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
            # Parses the LLM's ChatMessage output into a string
        )
        logger.info("RAG System initialized.")

    async def invoke_chain(self, question: str) -> str:
        """
        Invokes the RAG chain asynchronously with a given question.
        """
        try:
            logger.debug(f"Invoking RAG chain with question: {question}")
            # Use ainvoke for async operations with LCEL
            response = await self.rag_chain.ainvoke({"question": question})
            logger.debug(f"RAG chain response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error invoking RAG chain: {e}", exc_info=True)
            # Re-raise the exception to be handled by the caller
            raise


# Global instance is optional. For FastAPI or larger apps, dependency injection is preferred.
# Example:
rag_system_instance: RAGSystem | None = None


def get_rag_system_instance() -> RAGSystem:
    global rag_system_instance
    if rag_system_instance is None:
        # This will use the globally configured LLM and Retriever
        rag_system_instance = RAGSystem()
    return rag_system_instance


# Example Usage for standalone testing:
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv, find_dotenv
    from unittest.mock import patch  # For mocking
    from langchain_core.documents import Document  # For creating mock documents

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Running rag_pipeline.py standalone test...")

    env_path = find_dotenv()
    if env_path:
        logger.info(f"Loading .env file from: {env_path}")
        load_dotenv(dotenv_path=env_path)
        from app.config import Settings

        settings_instance = Settings()
        from app.config import settings as app_settings

        app_settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or app_settings.OPENAI_API_KEY
        app_settings.OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME") or app_settings.OPENAI_MODEL_NAME
    else:
        logger.warning("No .env file found. Relying on environment variables or defaults.")

    class MockRetriever(BaseRetriever):
        def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
            logger.info(f"[MockRetriever SYNC] Getting documents for: {query}")
            if "AVL tree" in query.lower():
                return [
                    Document(page_content="AVL trees are self-balancing binary search trees. Rotations are used to maintain balance after insertions or deletions."),
                    Document(page_content="There are four types of rotations in AVL trees: Left rotation (L), Right rotation (R), Left-Right rotation (LR), and Right-Left rotation (RL)."),
                ]
            return [Document(page_content="No specific information found for this query in mock data.")]

        async def _aget_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
            logger.info(f"[MockRetriever ASYNC] Getting documents for: {query}")
            await asyncio.sleep(0.1)
            if "AVL tree" in query.lower():
                return [
                    Document(
                        page_content="AVL trees are self-balancing binary search trees. Rotations (like left and right rotations) are key"
                        " operations to maintain their balance property after node insertions or deletions."
                    ),
                    Document(page_content="The balance factor of any node in an AVL tree is defined as height(left_subtree) - height(right_subtree) and must be in {-1, 0, 1}."),
                ]
            return [Document(page_content="Mock context: No specific information found for this query.")]

    async def main_test():
        logger.info("Starting RAG system test...")

        try:
            get_llm_instance()  # Ensures LLM provider is ready
        except RuntimeError as e:
            logger.error(f"Failed to get LLM instance: {e}. Cannot run RAG test.")
            return
        except ValueError as e:
            logger.error(f"Failed to initialize LLMProvider for RAG test: {e}. Check OPENAI_API_KEY.")
            return

        mock_retriever_instance = MockRetriever()
        with patch("app.core.rag_pipeline.get_retriever", return_value=mock_retriever_instance):
            try:
                rag_system = RAGSystem()

                test_question = "What are AVL tree rotations used for?"
                logger.info(f'Sending question to RAG system: "{test_question}"')

                answer = await rag_system.invoke_chain(test_question)
                logger.info(f"RAG Answer: {answer}")

                test_question_no_context = "What is the capital of France?"
                logger.info(f'Sending question with no context to RAG system: "{test_question_no_context}"')
                answer_no_context = await rag_system.invoke_chain(test_question_no_context)
                logger.info(f"RAG Answer (no context expected): {answer_no_context}")

            except RuntimeError as e:  # Catch errors from get_llm_instance if it failed
                logger.error(f"Runtime error during RAG system operation: {e}")
            except Exception as e:
                logger.error(f"Error during RAG system test: {e}", exc_info=True)

    try:
        asyncio.run(main_test())
    except Exception as e:
        logger.error(f"Error running main_test_async: {e}", exc_info=True)
