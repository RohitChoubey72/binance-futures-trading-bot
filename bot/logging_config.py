import logging
from pathlib import Path

def setup_logging() -> None:
    """
    Sets up application-wide logging.
    - DEBUG logs and above are written to logs/trading.log
    - INFO logs and above are printed to the console
    """
    project_root = Path(__file__).resolve().parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "trading.log"

    # Define formatters
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    # Create and configure file handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers in case of multiple calls
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Adjust external libraries noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
