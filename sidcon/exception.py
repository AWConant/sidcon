import logging
import traceback

logging.basicConfig()
logger = logging.getLogger(__name__)


def format_tb(e: Exception) -> str:
    return f"{''.join(traceback.format_tb(e.__traceback__))}{str(e)}"
