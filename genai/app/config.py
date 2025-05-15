# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    OPENAI_API_KEY: str = "YOUR_DEFAULT_API_KEY_IF_NOT_SET"
    OPENAI_EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"

    # WEAVIATE_URL: str = "http://localhost:8080"

    def __init__(self, **values):
        super().__init__(**values)
        if self.OPENAI_API_KEY == "YOUR_DEFAULT_API_KEY_IF_NOT_SET" or not self.OPENAI_API_KEY:
            logger.warning(
                "OPENAI_API_KEY is not set in .env file or environment variables. "
                "Using default placeholder which will likely fail."
            )

settings = Settings()

