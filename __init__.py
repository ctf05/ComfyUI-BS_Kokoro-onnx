import logging
import os

logger = logging.getLogger(__name__)

try:
    from .nodes import NODE_CLASS_MAPPINGS
    __all__ = ['NODE_CLASS_MAPPINGS']

except ImportError as e:
    missing_module = str(e).split(" ")[-1].replace("'", "")
    logger.error(f"ERROR: Could not import required library '{missing_module}'. Ensure the required packages are installed by running: pip install -r {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')}")
    NODE_CLASS_MAPPINGS = {}
    __all__ = ['NODE_CLASS_MAPPINGS']