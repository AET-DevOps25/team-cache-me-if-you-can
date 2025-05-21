import logging
import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
# from langchain_community.llms import GPT4All # Example for local LLM

from app.config import settings

logger = logging.getLogger(__name__)

class LLMProvider:
    """
    Provides an instance of a Language Model (LLM).
    Currently supports OpenAI chat models.
    """
    def __init__(self):
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "YOUR_DEFAULT_API_KEY_IF_NOT_SET":
            logger.error("OPENAI_API_KEY is not set correctly for LLM.")
            raise ValueError("OPENAI_API_KEY is required for OpenAI LLM.")

        self.llm: BaseChatModel = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL_NAME,
            temperature=settings.OPENAI_LLM_TEMPERATURE if hasattr(settings, 'OPENAI_LLM_TEMPERATURE') else 0.1, # Make temperature configurable
        )
        logger.info(f"Initialized ChatOpenAI provider with model: {settings.OPENAI_MODEL_NAME}")

    def get_model(self) -> BaseChatModel:
        """Returns the configured LLM instance."""
        return self.llm

try:
    llm_provider = LLMProvider()
except ValueError as e:
    logger.error(f"Failed to initialize LLMProvider: {e}")
    llm_provider = None

def get_llm_instance() -> BaseChatModel:
    """
    Returns the pre-configured LLM instance.
    Raises RuntimeError if the provider failed to initialize.
    """
    if llm_provider is None:
        logger.error("LLMProvider is not initialized. Check API keys and configuration.")
        raise RuntimeError("LLMProvider could not be initialized.")
    return llm_provider.get_model()

# Example usage:
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Running llm.py standalone test...")

    from dotenv import load_dotenv, find_dotenv
    env_path = find_dotenv()
    if env_path:
        logger.info(f"Loading .env file from: {env_path}")
        load_dotenv(dotenv_path=env_path)
        from app.config import Settings
        settings_instance = Settings()
        settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        settings.OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME") or settings.OPENAI_MODEL_NAME

        current_llm_provider = None
        try:
            current_llm_provider = LLMProvider()
        except ValueError as e_init:
            logger.error(f"Failed to initialize LLMProvider for test: {e_init}")
    else:
        logger.warning("No .env file found. Relying on environment variables or defaults.")
        current_llm_provider = llm_provider

    if not current_llm_provider:
        logger.error("Cannot run test: LLMProvider is not available.")
    else:
        try:
            llm = current_llm_provider.get_model()
            test_prompt = "Explain the concept of a Large Language Model in one sentence."
            logger.info(f"Sending prompt to LLM: \"{test_prompt}\"")
            
            from langchain_core.messages import HumanMessage
            response = llm.invoke(test_prompt) # LangChain often auto-wraps string to HumanMessage

            logger.info(f"LLM Response: {response.content}")
        except ValueError as e:
            logger.error(f"Configuration error during test: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during test: {e}", exc_info=True)