import logging
import os


def custom_path_filter(path: str) -> str:
    """
    Filters the provided file path to shorten it by removing the project root portion.
    """
    project_root = "project_20250805_1626_customer_bot"

    idx = path.find(project_root)
    if idx != -1:
        path = path[idx + len(project_root) :]
    return path


class CustomLogRecord(logging.LogRecord):
    """
    CustomLogRecord modifies the default LogRecord to filter and shorten the file path in log messages.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pathname = custom_path_filter(self.pathname)


def setup_logger(log_filename: str = "app.log", log_dir: str = "logs") -> logging.Logger:
    """
    Sets up and configures the logger with custom log record handling and file/stream handlers.
    """
    # Ensure the logging directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_filepath = os.path.join(log_dir, log_filename)

    # Check if we're in chat mode (quiet logging)
    chat_mode = os.getenv("ADVENTURE_CHAT_MODE", "false").lower() == "true"

    # Define the logging configuration
    logging.setLogRecordFactory(CustomLogRecord)

    # Create handlers
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    # In chat mode, only show WARNING and above on console
    stream_handler.setLevel(logging.WARNING if chat_mode else logging.INFO)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(module)s] [%(pathname)s]: %(message)s",
        handlers=[stream_handler, file_handler],
    )

    return logging.getLogger()


# Initialize the logger with the custom configuration
logger = setup_logger()
