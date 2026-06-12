import logging
from typing import Any, Dict
from bot.client import BinanceFuturesClient

logger = logging.getLogger(__name__)

def normalize_order_response(raw_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses and normalizes a raw Binance Futures API response into a consistent structure.
    
    Args:
        raw_response: The raw dictionary parsed from the Binance JSON response.
        
    Returns:
        A dict containing standard fields with appropriate types.
    """
    # Helper to parse string decimals from Binance to floats safely
    def to_float(val: Any, default: float = 0.0) -> float:
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    normalized = {
        "order_id": raw_response.get("orderId"),
        "client_order_id": raw_response.get("clientOrderId"),
        "symbol": raw_response.get("symbol"),
        "status": raw_response.get("status"),
        "side": raw_response.get("side"),
        "type": raw_response.get("type"),
        "quantity": to_float(raw_response.get("origQty")),
        "executed_quantity": to_float(raw_response.get("executedQty")),
        "price": to_float(raw_response.get("price")),
        "average_price": to_float(raw_response.get("avgPrice")),
        "time_in_force": raw_response.get("timeInForce"),
        "cum_quote": to_float(raw_response.get("cumQuote")),
        "update_time": raw_response.get("updateTime"),
    }
    
    logger.debug("Normalized order response: %s", normalized)
    return normalized

def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float
) -> Dict[str, Any]:
    """
    Places a MARKET order on Binance Futures (USDT-M).
    
    Args:
        client: The instantiated BinanceFuturesClient.
        symbol: The trading pair (e.g., BTCUSDT).
        side: The order direction (BUY or SELL).
        quantity: The order size.
        
    Returns:
        A normalized dictionary representing the order result.
    """
    logger.info("Preparing MARKET %s order for %s (Qty: %s)", side, symbol, quantity)
    
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": str(quantity),
    }
    
    raw_res = client.place_order(params)
    return normalize_order_response(raw_res)

def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC"
) -> Dict[str, Any]:
    """
    Places a LIMIT order on Binance Futures (USDT-M).
    
    Args:
        client: The instantiated BinanceFuturesClient.
        symbol: The trading pair (e.g., BTCUSDT).
        side: The order direction (BUY or SELL).
        quantity: The order size.
        price: The trigger price.
        time_in_force: The Time In Force policy (default: GTC).
        
    Returns:
        A normalized dictionary representing the order result.
    """
    logger.info("Preparing LIMIT %s order for %s (Qty: %s, Price: %s, TIF: %s)", 
                side, symbol, quantity, price, time_in_force)
    
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": str(quantity),
        "price": str(price),
        "timeInForce": time_in_force,
    }
    
    raw_res = client.place_order(params)
    return normalize_order_response(raw_res)
