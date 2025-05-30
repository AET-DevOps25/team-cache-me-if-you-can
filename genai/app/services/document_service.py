import logging
import io
from typing import Tuple, Optional

from app.document_handling.extractors import TextExtractor
from app.document_handling.parsers import get_document_parser, DocumentParser
from app.vector_store.weaviate_connector import get_weaviate_indexer, WeaviateIndexer
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    def __init__(self):
        self.text_extractor = TextExtractor()  # Assuming TextExtractor has no init args or gets them from settings
        self.document_parser: DocumentParser = get_document_parser()  # Get pre-configured parser
        self.weaviate_indexer: WeaviateIndexer = get_weaviate_indexer()  # Get pre-configured indexer
        logger.info("DocumentProcessingService initialized.")

    async def process_and_index_document(self, file_content: bytes, filename: str) -> Tuple[int, Optional[str]]:
        """
        Processes a document file (extracts text, splits, and indexes into Weaviate).
        Returns a tuple: (number_of_documents_indexed, error_message_if_any).
        """
        try:
            logger.info(f"Starting processing for document: {filename}")
            file_io = io.BytesIO(file_content)

            # 1. Extract text
            logger.debug(f"Extracting text from {filename}...")
            extracted_text = self.text_extractor.extract_text(file_io, filename)
            if not extracted_text:
                logger.warning(f"No text extracted from {filename}. Skipping further processing.")
                return 0, "No text could be extracted from the document."
            logger.info(f"Successfully extracted text from {filename}. Length: {len(extracted_text)}")

            # 2. Split text into documents
            # Pass filename in metadata for potential use in Weaviate
            doc_metadata = {"source": filename}
            logger.debug(f"Splitting text from {filename} into documents...")
            documents = self.document_parser.split_text_to_documents(extracted_text, metadata=doc_metadata)
            if not documents:
                logger.warning(f"Text from {filename} resulted in zero documents after splitting.")
                return 0, "Extracted text could not be split into documents."
            logger.info(f"Split text from {filename} into {len(documents)} documents.")

            # 3. Index documents into Weaviate
            logger.debug(f"Indexing {len(documents)} documents from {filename} into Weaviate...")
            # The WeaviateIndexer now handles the actual indexing call to
            # Weaviate client
            self.weaviate_indexer.index_documents(documents)
            logger.info(f"Successfully initiated indexing for {len(documents)} documents from {filename}.")

            return len(documents), None  # Success
        except ValueError as ve:
            logger.error(f"Unsupported file type for {filename}: {ve}", exc_info=True)
            return (
                0,
                f"Unsupported file type: {filename}. Only PDF, DOCX, PPTX are supported.",
            )
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}", exc_info=True)
            # In a production scenario, you might want to distinguish different
            # error types
            return 0, f"An unexpected error occurred while processing {filename}."


# Singleton instance (or use FastAPI dependency injection)
_document_processing_service_instance: Optional[DocumentProcessingService] = None


def get_document_processing_service() -> DocumentProcessingService:
    global _document_processing_service_instance
    if _document_processing_service_instance is None:
        _document_processing_service_instance = DocumentProcessingService()
    return _document_processing_service_instance


if __name__ == "__main__":
    # Basic test for DocumentProcessingService
    # This requires OPENAI_API_KEY for Weaviate text2vec-openai and a running
    # Weaviate instance.
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    from dotenv import load_dotenv, find_dotenv
    import os
    import asyncio

    env_path = find_dotenv()
    if env_path:
        logger.info(f"Loading .env file from: {env_path}")
        load_dotenv(dotenv_path=env_path, override=True)
        from app.config import Settings  # Re-init or update settings

        settings_instance = Settings()
        # Ensure global settings object is updated for other modules
        if os.getenv("OPENAI_API_KEY"):
            settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if os.getenv("WEAVIATE_URL"):
            settings.WEAVIATE_URL = os.getenv("WEAVIATE_URL")
    else:
        logger.warning("No .env file for service test. Relying on env vars or defaults.")

    async def test_service():
        service = get_document_processing_service()

        # Create a dummy PDF file content for testing
        # In a real test, you'd use a small, actual PDF, DOCX, or PPTX file.
        # For simplicity, we mock the content. A real PDF byte string is complex.
        # This will likely fail text extraction if not a valid PDF, but tests the flow.
        # Consider using a tiny, real PDF for better testing.
        dummy_pdf_content = (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 "
            b"0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n"
            b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length 44>>stream\nBT"
            b" /F1 24 Tf 100 700 Td (Hello World Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 "
            b"f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\n0000000210 00000 n\n0000000260 00000"
            b" n\ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n303\n%%EOF"
        )
        dummy_filename = "test_document.pdf"

        logger.info(f"Testing processing for {dummy_filename}")
        try:
            # Need to run get_weaviate_client once to ensure schema if testing
            # against live Weaviate
            from app.vector_store.weaviate_connector import get_weaviate_client

            get_weaviate_client()  # Ensures connection and schema

            docs_indexed, error = await service.process_and_index_document(dummy_pdf_content, dummy_filename)

            if error:
                logger.error(f"Service test failed for {dummy_filename}: {error}")
            else:
                logger.info(f"Service test successful for {dummy_filename}. Documents indexed: {docs_indexed}")
                assert docs_indexed > 0, "Expected at least one document to be indexed from test PDF content"

            # Test with an unsupported file type
            unsupported_filename = "test.txt"
            dummy_txt_content = b"This is a plain text file."
            docs_indexed_txt, error_txt = await service.process_and_index_document(dummy_txt_content, unsupported_filename)
            logger.info(f"Service test for {unsupported_filename}: Docs={docs_indexed_txt}, Error='{error_txt}'")
            assert error_txt is not None and "Unsupported file type" in error_txt, "Expected error for unsupported .txt file"
            assert docs_indexed_txt == 0

        except RuntimeError as re:
            logger.error(f"RuntimeError during service test, possibly Weaviate connection: {re}")
        except Exception as e:
            logger.error(f"Unexpected error during service test: {e}", exc_info=True)

    if __name__ == "__main__":
        asyncio.run(test_service())
