import logging
import os

from app.config import settings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

# from langchain_community.llms import GPT4All # Example for local LLM

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Provides an instance of a Language Model (LLM).
    Currently supports OpenAI chat models.
    """

    def __init__(self):
        self.llm: BaseChatModel = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL_NAME,
            temperature=(settings.OPENAI_LLM_TEMPERATURE if hasattr(settings, "OPENAI_LLM_TEMPERATURE") else 0.1),
        )
        logger.info(f"Initialized ChatOpenAI provider with model: {settings.OPENAI_MODEL_NAME}")

    def get_model(self) -> BaseChatModel:
        """Returns the configured LLM instance."""
        return self.llm


_llm_provider_singleton: LLMProvider | None = None


def get_llm_instance() -> BaseChatModel:
    """
    Returns the pre-configured LLM instance.
    Initializes the provider on first call if needed, using current app.config.settings.
    Raises RuntimeError if the provider failed to initialize.
    """
    global _llm_provider_singleton
    if _llm_provider_singleton is None:
        logger.info("LLMProvider singleton is None. Attempting to initialize now...")
        try:
            _llm_provider_singleton = LLMProvider()
            logger.info("LLMProvider singleton initialized successfully.")
        except ValueError as e:
            logger.error(f"Failed to initialize LLMProvider during get_llm_instance: {e}")
            raise RuntimeError(f"LLMProvider could not be initialized: {e}")
        except Exception as e:  # Catch any other unexpected errors during init
            logger.error(
                f"Unexpected error initializing LLMProvider in get_llm_instance: {e}",
                exc_info=True,
            )
            raise RuntimeError(f"Unexpected error during LLMProvider initialization: {e}")

    return _llm_provider_singleton.get_model()


def reset_llm_provider_for_testing():
    """
    Resets the global LLM provider singleton.
    This is intended for testing purposes to allow re-initialization
    with potentially different configurations loaded by a test setup.
    """
    global _llm_provider_singleton
    _llm_provider_singleton = None
    logger.info("Global LLMProvider singleton has been reset for testing.")


# Example usage:
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Running llm.py standalone test...")

    from dotenv import load_dotenv, find_dotenv

    env_path = find_dotenv()
    if env_path:
        logger.info(f"Loading .env file from: {env_path}")
        load_dotenv(dotenv_path=env_path, override=True)

        import app.config

        api_key_from_env = os.getenv("OPENAI_API_KEY")
        if api_key_from_env:
            app.config.settings.OPENAI_API_KEY = api_key_from_env

        model_name_from_env = os.getenv("OPENAI_MODEL_NAME")
        if model_name_from_env:
            app.config.settings.OPENAI_MODEL_NAME = model_name_from_env

        key_is_set = bool(
            app.config.settings.OPENAI_API_KEY
            and app.config.settings.OPENAI_API_KEY
            not in [
                "YOUR_DEFAULT_PLACEHOLDER",
                "YOUR_DEFAULT_API_KEY_IF_NOT_SET",
            ]
        )
        logger.info(f"Updated app.config.settings for test: KEY set: {key_is_set}, Model: {app.config.settings.OPENAI_MODEL_NAME}")

        reset_llm_provider_for_testing()
    else:
        logger.warning("No .env file found for llm.py test. Relying on existing environment variables or defaults.")
        reset_llm_provider_for_testing()

    llm = get_llm_instance()
    test_prompt = "Explain the concept of a Large Language Model in one sentence."
    logger.info(f'Sending prompt to LLM: "{test_prompt}"')

    response = llm.invoke(test_prompt)

    response_content = response.content if hasattr(response, "content") else str(response)
    logger.info(f"LLM Response: {response_content}")
