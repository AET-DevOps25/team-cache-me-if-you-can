import asyncio
import logging
from typing import List

from app.core.llm import get_llm_instance
from app.vector_store.weaviate_connector import get_retriever
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# A machine-readable identifier for when the context is not useful.
CONTEXT_NOT_FOUND_IDENTIFIER = "CONTEXT_NOT_FOUND"

def format_docs(docs: List[Document]) -> str:
    """A simple function to join the page content of retrieved documents."""
    return "\n\n".join(doc.page_content for doc in docs)


class RAGSystem:
    """
    Implements a Retrieval Augmented Generation (RAG) system.
    Combines a retriever, a prompt template, and an LLM to answer questions.
    """

    def __init__(self, llm: BaseChatModel = None, retriever: BaseRetriever = None):
        self.llm = llm or get_llm_instance()
        self.retriever = retriever or get_retriever()

        # Define a prompt template for the RAG chain
        rag_template = """
        You are an AI assistant for the StudySync platform. Your goal is to help students understand their course material.
        Answer the question strictly and only based on the provided context.

        When you find the answer in the context, cite the source. The context for each document chunk is preceded by its source and page number in the format 'source: [source], page: [page_number]'.
        At the end of the sentence or paragraph that uses information from the context, add a citation like `[Source: document_name.pdf, Page: 12]`.

        If the provided context does not contain the information needed to answer the question, you MUST respond with only the following exact phrase:
        {context_not_found_identifier}

        Context:
        {context}

        Question: {question}

        Answer:
        """
        self.rag_prompt = ChatPromptTemplate.from_template(rag_template)

        # General knowledge prompt, used when context is not found
        general_knowledge_template = """
        You are an AI assistant. You were asked a question but could not find the answer in the user's provided documents.
        Provide a helpful, general-knowledge answer to the following question.

        Question: {question}

        Answer:
        """
        self.general_knowledge_prompt = ChatPromptTemplate.from_template(general_knowledge_template)

        # The primary RAG chain
        self.rag_chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough(),
                "context_not_found_identifier": lambda _: CONTEXT_NOT_FOUND_IDENTIFIER,
            }
            | self.rag_prompt
            | self.llm
            | StrOutputParser()
        )

        # A separate chain for generating answers from general knowledge
        self.general_knowledge_chain = self.general_knowledge_prompt | self.llm | StrOutputParser()

        logger.info("RAG System initialized.")

    async def invoke_chain(self, question: str) -> dict:
        """
        Invokes the RAG chain and, if necessary, the general knowledge chain.
        Returns a dictionary with the answer and the source documents.
        """
        logger.debug(f"Invoking RAG chain with question: {question}")

        # Get the source documents first, so we can return them regardless of the answer
        source_documents = await self.retriever.aget_relevant_documents(question)
        # Manually format the context with source information for the prompt
        formatted_context = "\n\n".join(
            f"source: {doc.metadata.get('source', 'Unknown')}, page: {doc.metadata.get('page_number', 'N/A')}\n{doc.page_content}"
            for doc in source_documents
        )

        # Invoke the RAG chain with the manually formatted context
        rag_answer = await self.rag_chain.ainvoke({"question": question, "context": formatted_context})

        final_answer = ""
        if CONTEXT_NOT_FOUND_IDENTIFIER in rag_answer:
            logger.info(f"Context not found for question: '{question}'. Switching to general knowledge.")
            general_answer = await self.general_knowledge_chain.ainvoke({"question": question})
            final_answer = (
                "I could not find a definitive answer in your documents. "
                f"However, based on my general knowledge:\n\n{general_answer}"
            )
        else:
            final_answer = rag_answer

        logger.debug(f"Final answer: {final_answer}")
        return {"answer": final_answer, "source_documents": source_documents}


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
