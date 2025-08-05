import json
import os
from typing import Any, Dict, Optional

from src.common.logging import logger


def load_json(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load a JSON file and return its contents.
    """
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        logger.error(f"File '{filename}' contains invalid JSON.")
        return None
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        raise


def save_json(filename: str, data: Dict[str, Any]) -> None:
    """
    Save data to a JSON file.
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            json.dump(data, file, indent=2)
        logger.info(f"Data saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving JSON file: {e}")
        raise


def ensure_directory_exists(path: str) -> None:
    """
    Ensure that the directory exists, creating it if it doesn't.
    """
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Directory ensured at: {path}")
    except OSError as e:
        logger.error(f"Failed to create directory at {path}: {str(e)}")
        raise
