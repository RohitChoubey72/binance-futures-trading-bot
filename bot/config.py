import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve paths
BOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BOT_DIR.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load environment variables from .env file
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Extract configurations
BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "").strip()
BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "").strip()
BASE_URL: str = os.getenv("BASE_URL", "https://testnet.binancefuture.com").strip().rstrip("/")

def validate_config() -> None:
    """
    Validates that the necessary API credentials and configurations are correctly set.
    Raises:
        ValueError: If configuration values are missing or default placeholders are used.
    """
    missing_vars = []
    
    if not BINANCE_API_KEY or BINANCE_API_KEY == "your_api_key_here":
        missing_vars.append("BINANCE_API_KEY")
    if not BINANCE_SECRET_KEY or BINANCE_SECRET_KEY == "your_secret_key_here":
        missing_vars.append("BINANCE_SECRET_KEY")
        
    if missing_vars:
        raise ValueError(
            f"Missing or default configuration keys found: {', '.join(missing_vars)}. "
            f"Please set them in your .env file at: {ENV_PATH}"
        )
