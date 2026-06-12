import hmac
import hashlib
import time
import logging
from typing import Any, Dict
from urllib.parse import urlencode
import httpx

logger = logging.getLogger(__name__)

class BinanceClientError(Exception):
    """Base exception for all Binance client issues."""
    pass

class BinanceNetworkError(BinanceClientError):
    """Exception raised when a network issue occurs."""
    pass

class BinanceAPIError(BinanceClientError):
    """Exception raised when Binance API returns an error response."""
    def __init__(self, status_code: int, code: int, message: str):
        super().__init__(f"API Error (Status {status_code}): Code {code} - {message}")
        self.status_code = status_code
        self.code = code
        self.message = message

class BinanceFuturesClient:
    """
    Direct REST API Client for Binance Futures Testnet.
    Handles authentication, signing, and request execution.
    """
    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")
        # Using a persistent httpx client for connection pooling
        self.client = httpx.Client(timeout=15.0)
        logger.debug("BinanceFuturesClient initialized with base URL: %s", self.base_url)

    def __enter__(self) -> "BinanceFuturesClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Closes the underlying HTTP client session."""
        self.client.close()
        logger.debug("BinanceFuturesClient HTTP connection closed.")

    def _sign(self, query_string: str) -> str:
        """Generates HMAC-SHA256 signature for the given query string."""
        return hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def _prepare_payload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches order parameters with a timestamp and calculates the HMAC signature.
        """
        payload = params.copy()
        # Add required timestamp (in milliseconds)
        payload["timestamp"] = int(time.time() * 1000)
        
        # Binance requires signature to be generated from the exact query string format
        query_string = urlencode(payload)
        signature = self._sign(query_string)
        payload["signature"] = signature
        return payload

    def place_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a signed POST request to create an order (/fapi/v1/order).
        
        Args:
            params: Dictionary containing order placement parameters.
            
        Returns:
            Dictionary containing the API JSON response.
            
        Raises:
            BinanceAPIError: If the server returns a non-2xx status code.
            BinanceNetworkError: If a connection/network timeout occurs.
            BinanceClientError: For any other unexpected errors.
        """
        url = f"{self.base_url}/fapi/v1/order"
        headers = {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = self._prepare_payload(params)
        logger.debug("Placing order, URL: %s, Payload keys: %s", url, list(payload.keys()))

        try:
            # We send data as form url-encoded per Binance requirements
            response = self.client.post(url, headers=headers, data=payload)
            response.raise_for_status()
            
            data: Dict[str, Any] = response.json()
            logger.debug("Order response successfully received: %s", data)
            return data
            
        except httpx.HTTPStatusError as e:
            try:
                error_json = e.response.json()
                code = error_json.get("code", 0)
                msg = error_json.get("msg", "Unknown Binance API Error")
            except Exception:
                code = 0
                msg = e.response.text or str(e)
            
            logger.error("Binance API error response: Status %d - Code %d: %s", 
                         e.response.status_code, code, msg)
            raise BinanceAPIError(status_code=e.response.status_code, code=code, message=msg) from e
            
        except httpx.RequestError as e:
            logger.error("Network error while trying to connect to Binance: %s", str(e))
            raise BinanceNetworkError(f"Network error communicating with Binance Futures: {e}") from e
            
        except Exception as e:
            logger.error("Unexpected error in client request execution: %s", str(e))
            raise BinanceClientError(f"An unexpected error occurred: {e}") from e
