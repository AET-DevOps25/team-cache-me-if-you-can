from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging
from typing import List

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parses extracted text into manageable chunks (Documents for LangChain)."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initializes the text splitter.
        Args:
            chunk_size: The maximum number of characters in each chunk.
            chunk_overlap: The number of characters to overlap between chunks.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            # add_start_index=True, # Useful for some RAG strategies
        )
        logger.info(
            f"DocumentParser initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )

    def split_text_to_documents(
        self, text: str, metadata: dict = None
    ) -> List[Document]:
        """
        Splits a long text into smaller Document objects.
        Args:
            text: The text content to split.
            metadata: Optional metadata to associate with each created Document.
                      This metadata can include source filename, page numbers, etc.
        Returns:
            A list of LangChain Document objects.
        """
        if not text:
            logger.warning("Attempted to split empty text. Returning empty list.")
            return []

        base_metadata = metadata or {}

        split_texts = self.text_splitter.split_text(text)

        documents = []
        for i, chunk_text in enumerate(split_texts):
            # Create specific metadata for each chunk if needed
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = (
                i  # Example of adding chunk-specific metadata
            )
            # You might add more sophisticated metadata like original page numbers if available from extractor

            doc = Document(page_content=chunk_text, metadata=chunk_metadata)
            documents.append(doc)

        logger.info(f"Split text into {len(documents)} documents.")
        return documents


# Global instance (or inject as dependency)
document_parser = DocumentParser()


def get_document_parser() -> DocumentParser:
    return document_parser
