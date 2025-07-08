import logging
from typing import List
from langchain_core.documents import Document
from app.core.llm import get_llm_instance
from langchain_core.language_models import BaseChatModel
from langchain.chains.summarize import load_summarize_chain
from app.vector_store.weaviate_connector import get_all_documents_for_source

logger = logging.getLogger(__name__)


class SummarizationService:
    def __init__(self, llm: BaseChatModel = None):
        self.llm = llm or get_llm_instance()
        # Initialize the summarization chain.
        # "map_reduce" is effective for large documents.
        self.summary_chain = load_summarize_chain(
            self.llm,
            chain_type="map_reduce",
            # You can customize prompts if needed, for now using defaults
            # map_prompt=...
            # combine_prompt=...
        )
        logger.info("SummarizationService initialized.")

    async def summarize_document(self, source_filename: str) -> str:
        """
        Generates a summary for a given document by its source filename.
        """
        logger.info(f"Starting summarization for document: {source_filename}")

        # 1. Retrieve all document chunks
        document_chunks: List[Document] = await get_all_documents_for_source(source_filename)

        if not document_chunks:
            logger.warning(f"No document chunks found for '{source_filename}'. Cannot generate summary.")
            return "Could not find the document to summarize. Please ensure it has been uploaded and processed."

        logger.info(f"Found {len(document_chunks)} chunks for summarization.")

        # 2. Run the summarization chain
        try:
            # The chain will run the map-reduce process under the hood.
            result = await self.summary_chain.arun(document_chunks)
            logger.info(f"Successfully generated summary for {source_filename}.")
            return result
        except Exception as e:
            logger.error(f"Error during summarization for {source_filename}: {e}", exc_info=True)
            return f"An error occurred while generating the summary: {e}"


def get_summarization_service() -> SummarizationService:
    # Basic factory function, can be improved with singleton pattern or DI
    return SummarizationService() 