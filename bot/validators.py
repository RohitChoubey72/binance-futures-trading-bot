import re
from typing import Optional

def validate_symbol(symbol: str) -> None:
    """
    Validates that the symbol is in uppercase and matches standard Binance ticker patterns.
    E.g. BTCUSDT, ETHUSDT.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    
    # Check for standard Binance symbol pattern: alphanumeric, uppercase, 3 to 12 chars
    pattern = r"^[A-Z0-9]{3,12}$"
    if not re.match(pattern, symbol):
        raise ValueError(
            f"Invalid symbol format: '{symbol}'. "
            "Symbol must be uppercase alphanumeric and between 3 to 12 characters (e.g., BTCUSDT)."
        )

def validate_side(side: str) -> None:
    """Validates that side is either BUY or SELL."""
    valid_sides = {"BUY", "SELL"}
    if side not in valid_sides:
        raise ValueError(f"Invalid side: '{side}'. Must be one of: {', '.join(valid_sides)}.")

def validate_type(order_type: str) -> None:
    """Validates that order type is either MARKET or LIMIT."""
    valid_types = {"MARKET", "LIMIT"}
    if order_type not in valid_types:
        raise ValueError(f"Invalid order type: '{order_type}'. Must be one of: {', '.join(valid_types)}.")

def validate_quantity(quantity: float) -> None:
    """Validates that the quantity is a positive number."""
    if quantity <= 0:
        raise ValueError(f"Quantity must be a positive number. Got: {quantity}")

def validate_price(price: Optional[float], order_type: str) -> None:
    """
    Validates that price is provided and positive for LIMIT orders, 
    and raises an error if price is erroneously provided for MARKET orders.
    """
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        if price <= 0:
            raise ValueError(f"Price must be a positive number for LIMIT orders. Got: {price}")
    elif order_type == "MARKET":
        if price is not None:
            raise ValueError("Price should not be provided for MARKET orders.")

def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None
) -> None:
    """
    Aggregates validation of all parameters required for ordering.
    """
    validate_symbol(symbol)
    validate_side(side)
    validate_type(order_type)
    validate_quantity(quantity)
    validate_price(price, order_type)
