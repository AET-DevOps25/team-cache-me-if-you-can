import logging
import sys
from app.config import settings  # To get LOG_LEVEL and ENVIRONMENT


def setup_logging():
    """Configures logging for the application."""
    log_level = settings.LOG_LEVEL.upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],  # Log to stdout, suitable for containers
    )

    # Adjust logging levels for noisy libraries if needed
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("httpcore").setLevel(logging.WARNING)
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING) # Can be very verbose

    logger = logging.getLogger(settings.APP_NAME)
    logger.info(
        f"Logging configured with level: {log_level} in {settings.ENVIRONMENT} environment."
    )