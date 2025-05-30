import logging
from typing import List, Optional, Any

import weaviate
import weaviate.classes as wvc
from app.config import settings
from app.core.embeddings import get_embedding_model_instance
from langchain_core.documents import (
    Document as LangchainDocument,
)
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from weaviate.exceptions import (
    WeaviateClosedClientError,
    WeaviateConnectionError,
)

logger = logging.getLogger(__name__)

_weaviate_client: Optional[weaviate.WeaviateClient] = None
DEFAULT_TOP_K = 5


def get_weaviate_client() -> weaviate.WeaviateClient:
    """Initializes and returns a Weaviate v4 client instance."""
    global _weaviate_client
    if _weaviate_client is None or not _weaviate_client.is_connected():
        logger.info(f"Attempting to connect to Weaviate at {settings.WEAVIATE_URL}")
        headers = {}
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY not in [
            "YOUR_DEFAULT_API_KEY_IF_NOT_SET",
            "",
        ]:
            headers["X-OpenAI-Api-Key"] = settings.OPENAI_API_KEY

        # Assuming local Weaviate instance defined by WEAVIATE_URL (e.g.,
        # "http://localhost:8080")
        http_host = settings.WEAVIATE_URL.split(":")[1].replace("//", "") if "://" in settings.WEAVIATE_URL else "localhost"
        http_port = int(settings.WEAVIATE_URL.split(":")[2]) if len(settings.WEAVIATE_URL.split(":")) > 2 else 8080
        grpc_port = 50051

        try:
            _weaviate_client = weaviate.connect_to_custom(
                http_host=http_host,
                http_port=http_port,
                http_secure=settings.WEAVIATE_URL.startswith("https"),
                grpc_host=http_host,
                grpc_port=grpc_port,
                grpc_secure=settings.WEAVIATE_URL.startswith("https"),
                headers=headers,
                # Timeout settings can be added via additional_config
                # additional_config=wvc.init.AdditionalConfig(
                #     timeout=wvc.init.Timeout(init=2, query=45, insert=60)
                # )
            )
            _weaviate_client.connect()

            if not _weaviate_client.is_ready():
                raise WeaviateConnectionError("Weaviate client connected but instance is not ready.")

            logger.info(f"Successfully connected to Weaviate v4 client at {settings.WEAVIATE_URL}.")
            ensure_weaviate_schema(client=_weaviate_client, index_name=settings.WEAVIATE_INDEX_NAME)
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate or ensure schema: {e}", exc_info=True)
            _weaviate_client = None  # Reset on failure
            raise RuntimeError(f"Could not initialize Weaviate client: {e}") from e

    return _weaviate_client


def ensure_weaviate_schema(client: weaviate.WeaviateClient, index_name: str):
    """
    Ensures that the specified Weaviate collection (schema) exists, creating it if necessary.
    Uses v4 client API.
    """
    try:
        if not client.collections.exists(index_name):
            logger.info(f"Collection '{index_name}' does not exist. Creating now...")

            # Define properties for the collection.
            # The 'text' property will store the document content.
            properties = [
                wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="source", data_type=wvc.config.DataType.TEXT),  # Example: filename
                wvc.config.Property(name="chunk_index", data_type=wvc.config.DataType.INT),  # Example
                # Add other metadata properties as needed. Ensure they are
                # simple types.
            ]

            vectorizer_config = wvc.config.Configure.Vectorizer.text2vec_openai(
                model=settings.OPENAI_EMBEDDING_MODEL_NAME,  # type="text", # Usually default
            )

            client.collections.create(
                name=index_name,
                properties=properties,
                vectorizer_config=vectorizer_config,
                # generative_config=generative_config, # If using Weaviate's generative search
                # Can add other configurations like vector_index_config, sharding_config, etc.
            )
            logger.info(f"Successfully created collection '{index_name}'.")
        else:
            logger.info(f"Collection '{index_name}' already exists.")
    except Exception as e:
        logger.error(f"Error ensuring Weaviate schema for '{index_name}': {e}", exc_info=True)
        raise


class WeaviateIndexer:
    """Handles indexing of Langchain Documents into Weaviate using v4 client."""

    def __init__(self, client: weaviate.WeaviateClient, index_name: str, batch_size: int = 100):
        self.client = client
        self.index_name = index_name
        self.batch_size = batch_size
        logger.info(f"WeaviateIndexer initialized for collection '{index_name}' with batch_size={batch_size}.")

    def index_documents(self, documents: List[LangchainDocument]):
        """
        Indexes a list of Langchain Documents into the Weaviate collection.
        Uses v4 batching.
        """
        if not documents:
            logger.info("No documents provided for indexing.")
            return

        try:
            collection = self.client.collections.get(self.index_name)
            # For v4, batching is typically done via the collection object
            with collection.batch.fixed_size(batch_size=self.batch_size) as batch:
                for i, doc in enumerate(documents):
                    properties = {"text": doc.page_content}
                    # Add metadata from LangchainDocument to properties
                    if doc.metadata:
                        for key, value in doc.metadata.items():
                            # Ensure metadata keys are valid property names and
                            # values are compatible types
                            if isinstance(value, (str, int, float, bool, list)):  # Weaviate supports list of primitives
                                properties[key.lower().replace(" ", "_")] = value  # else:  # logger.warning(f"Skipping metadata key '{key}' with unhandled type {type(value)}")

                    # If embeddings are generated outside Weaviate (e.g., by Langchain)
                    # and you want to provide them directly:
                    # vector = get_embedding_model_instance().embed_query(doc.page_content)
                    # batch.add_object(properties=properties, vector=vector)

                    batch.add_object(properties=properties)

                    if (i + 1) % self.batch_size == 0:
                        logger.info(f"Added {(i + 1)}/{len(documents)} documents to current Weaviate batch.")

            if collection.batch.failed_objects:
                logger.error(f"Failed to index {len(collection.batch.failed_objects)} documents.")
                for failed_obj in collection.batch.failed_objects:
                    logger.error(f"  Failed object: {failed_obj.message}, original: {failed_obj.original_uuid}, properties: {failed_obj.original_properties}")
            else:
                logger.info(f"Successfully indexed {len(documents)} documents into '{self.index_name}'.")

        except Exception as e:
            logger.error(f"Error indexing documents into '{self.index_name}': {e}", exc_info=True)
            raise


def get_weaviate_indexer() -> WeaviateIndexer:
    """Provides a WeaviateIndexer instance."""
    client = get_weaviate_client()
    return WeaviateIndexer(client, settings.WEAVIATE_INDEX_NAME)


class WeaviateLangchainRetriever(BaseRetriever):
    """Custom Langchain compatible retriever using Weaviate direct client for v4."""

    client: weaviate.WeaviateClient
    embedding_model: Embeddings
    index_name: str
    k: int

    def __init__(
        self,
        client: weaviate.WeaviateClient,
        embedding_model: Embeddings,
        index_name: str,
        k: int = DEFAULT_TOP_K,
    ):
        super().__init__(client=client, embedding_model=embedding_model, index_name=index_name, k=k)
        if not self.client.is_ready():
            logger.error("Weaviate client is not ready in WeaviateLangchainRetriever.")

    def _get_relevant_documents(self, query: str, **kwargs: Any) -> List[LangchainDocument]:
        """Retrieve relevant documents from Weaviate based on the query."""
        try:
            query_vector = self.embedding_model.embed_query(query)
            collection = self.client.collections.get(self.index_name)

            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=self.k,
                return_metadata=wvc.query.MetadataQuery(distance=True),
                # Example metadata
                return_properties=[
                    "text",
                    "source",
                    "chunk_index",
                ],
                # Specify properties to retrieve
            )

            documents = []
            for item in response.objects:
                content = item.properties.get("text", "")
                metadata = {
                    "source": item.properties.get("source"),
                    "chunk_index": item.properties.get("chunk_index"),
                }
                # Filter out None metadata values
                metadata = {k: v for k, v in metadata.items() if v is not None}
                if item.metadata and item.metadata.distance is not None:
                    metadata["distance"] = item.metadata.distance

                documents.append(LangchainDocument(page_content=content, metadata=metadata))

            logger.info(f"Retrieved {len(documents)} documents from '{self.index_name}' for query: '{query}'")
            return documents
        except WeaviateClosedClientError:
            logger.error("Weaviate client is closed. Attempting to reconnect and retry.")
            # Attempt to re-initialize the global client and retry once.
            global _weaviate_client
            _weaviate_client = None  # Force re-initialization
            self.client = get_weaviate_client()  # Re-assign client
            # This is a simplified retry, real-world might need more robust
            # handling
            return self._get_relevant_documents(query, **kwargs)
        except Exception as e:
            logger.error(f"Error retrieving documents from Weaviate: {e}", exc_info=True)
            return []  # Return empty list on error

    async def _aget_relevant_documents(self, query: str, **kwargs: Any) -> List[LangchainDocument]:
        logger.warning("Async retrieval called, using synchronous implementation as fallback.")
        return self._get_relevant_documents(query, **kwargs)


def get_retriever(k: int = DEFAULT_TOP_K) -> BaseRetriever:
    """Initializes and returns a WeaviateLangchainRetriever instance."""
    client = get_weaviate_client()
    embeddings = get_embedding_model_instance()
    # Pass k to the constructor
    return WeaviateLangchainRetriever(
        client=client,
        embedding_model=embeddings,
        index_name=settings.WEAVIATE_INDEX_NAME,
        k=k,
    )


def close_weaviate_connection():
    """Closes the global Weaviate client connection if it's open."""
    global _weaviate_client
    if _weaviate_client and _weaviate_client.is_connected():
        try:
            _weaviate_client.close()
            logger.info("Weaviate client connection closed.")
        except Exception as e:
            logger.error(f"Error closing Weaviate client connection: {e}", exc_info=True)
    _weaviate_client = None


if __name__ == "__main__":
    # Example usage for testing the connector
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Ensure .env is loaded if running standalone for API keys
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(), override=True)
    # You might need to explicitly update settings object if it's already
    # instantiated elsewhere
    settings.OPENAI_API_KEY = weaviate.util.get_env_var("OPENAI_API_KEY", "")  # Example of safe env var access
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not found in environment for standalone test.")

    test_index_name = "TestStudySyncIndexPyV4"  # Use a distinct test index
    original_index_name = settings.WEAVIATE_INDEX_NAME
    settings.WEAVIATE_INDEX_NAME = test_index_name

    try:
        logger.info(f"--- Test: Initializing Weaviate Client and Schema for '{test_index_name}' ---")
        client = get_weaviate_client()  # This will also call ensure_weaviate_schema

        if client.is_connected():
            logger.info("Client connected successfully.")

            logger.info("--- Test: Indexing Documents ---")
            indexer = get_weaviate_indexer()  # Will use test_index_name due to settings modification

            sample_docs_lc = [
                LangchainDocument(
                    page_content="Apollo 11 was the spaceflight that first landed humans on the Moon.",
                    metadata={"source": "nasa.txt", "chunk_index": 0},
                ),
                LangchainDocument(
                    page_content="Neil Armstrong was the first person to walk on the moon.",
                    metadata={"source": "history.txt", "chunk_index": 1},
                ),
                LangchainDocument(
                    page_content="The mission's commander was Neil Armstrong, the lunar module pilot was Buzz Aldrin.",
                    metadata={"source": "crew.txt", "chunk_index": 0},
                ),
            ]
            indexer.index_documents(sample_docs_lc)

            import time

            time.sleep(2)

            logger.info("--- Test: Retrieving Documents ---")
            retriever = get_retriever(k_results=2)
            query = "Who was on Apollo 11?"
            retrieved_docs = retriever.get_relevant_documents(query)

            logger.info(f"Query: {query}")
            if retrieved_docs:
                for i, doc in enumerate(retrieved_docs):
                    logger.info(f"  Retrieved Doc {i + 1}: {doc.page_content} (Metadata: {doc.metadata})")
            else:
                logger.info("  No documents retrieved.")

            query2 = "What was Apollo 11?"
            retrieved_docs2 = retriever.get_relevant_documents(query2)
            logger.info(f"Query: {query2}")
            if retrieved_docs2:
                for i, doc in enumerate(retrieved_docs2):
                    logger.info(f"  Retrieved Doc {i + 1}: {doc.page_content} (Metadata: {doc.metadata})")

        else:
            logger.error("Failed to connect client for testing.")

    except Exception as e:
        logger.error(f"An error occurred during the Weaviate connector test: {e}", exc_info=True)
    finally:
        logger.info(f"--- Test: Cleaning up collection '{test_index_name}' ---")
        if _weaviate_client and _weaviate_client.is_connected():
            if _weaviate_client.collections.exists(test_index_name):
                _weaviate_client.collections.delete(test_index_name)
                logger.info(f"Test collection '{test_index_name}' deleted.")

        settings.WEAVIATE_INDEX_NAME = original_index_name
        close_weaviate_connection()
        logger.info("--- Weaviate Connector Test Finished ---")
