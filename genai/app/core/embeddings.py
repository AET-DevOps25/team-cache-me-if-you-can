import logging
import os

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

# from langchain_community.embeddings import HuggingFaceInstructEmbeddings

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """
    Provides an instance of an embedding model.
    Currently supports OpenAI embeddings.
    """

    def __init__(self):
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "YOUR_DEFAULT_API_KEY_IF_NOT_SET":
            logger.error("OPENAI_API_KEY is not set correctly for embeddings.")
            raise ValueError("OPENAI_API_KEY is required for OpenAI Embeddings.")

        self.embedding_model: Embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_EMBEDDING_MODEL_NAME,
        )
        logger.info(f"Initialized OpenAIEmbeddings provider with model: {settings.OPENAI_EMBEDDING_MODEL_NAME}")

    def get_model(self) -> Embeddings:
        """Returns the configured embedding model instance."""
        return self.embedding_model


try:
    embedding_provider = EmbeddingProvider()
except ValueError as e:
    logger.error(f"Failed to initialize EmbeddingProvider: {e}")
    embedding_provider = (
        # Handle cases where initialization might fail (e.g. missing API key)
        None
    )


def get_embedding_model_instance() -> Embeddings:
    """
    Returns the pre-configured embedding model instance.
    Raises RuntimeError if the provider failed to initialize.
    """
    if embedding_provider is None:
        logger.error("EmbeddingProvider is not initialized. Check API keys and configuration.")
        raise RuntimeError("EmbeddingProvider could not be initialized.")
    return embedding_provider.get_model()


# Example usage:
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Running embeddings.py standalone test...")

    # Attempt to load .env file using find_dotenv to locate it
    from dotenv import load_dotenv, find_dotenv

    env_path = find_dotenv()
    if env_path:
        logger.info(f"Loading .env file from: {env_path}")
        load_dotenv(dotenv_path=env_path)
        from app.config import Settings

        settings_instance = Settings()
        settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        settings.OPENAI_EMBEDDING_MODEL_NAME = os.getenv("OPENAI_EMBEDDING_MODEL_NAME") or settings.OPENAI_EMBEDDING_MODEL_NAME

        current_embedding_provider = None
        try:
            current_embedding_provider = EmbeddingProvider()
        except ValueError as e_init:
            logger.error(f"Failed to initialize EmbeddingProvider for test: {e_init}")

    else:
        logger.warning("No .env file found. Relying on environment variables or defaults.")
        current_embedding_provider = embedding_provider  # Use the globally initialized one

    if not current_embedding_provider:
        logger.error("Cannot run test: EmbeddingProvider is not available.")
    else:
        try:
            embedder = current_embedding_provider.get_model()
            sample_text = "This is a test sentence for checking embeddings."
            embedding_vector = embedder.embed_query(sample_text)
            logger.info(f"Embedding for '{sample_text}':")
            logger.info(f"  Length: {len(embedding_vector)}")
            logger.info(f"  First 5 dims: {embedding_vector[:5]}")

            documents = [
                "This is the first document.",
                "This is a different, second document.",
            ]
            doc_embeddings = embedder.embed_documents(documents)
            logger.info(f"\nNumber of document embeddings: {len(doc_embeddings)}")
            if doc_embeddings:
                logger.info(f"Embedding for '{documents[0]}':")
                logger.info(f"  Length: {len(doc_embeddings[0])}")
                logger.info(f"  First 5 dims: {doc_embeddings[0][:5]}")

        except ValueError as e:
            logger.error(f"Configuration error during test: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during test: {e}", exc_info=True)
