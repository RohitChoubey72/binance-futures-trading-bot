import argparse
import sys
import logging
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from bot.validators import validate_order_inputs
from bot import config
from bot.client import BinanceFuturesClient, BinanceClientError
from bot.orders import place_market_order, place_limit_order
from bot.logging_config import setup_logging

logger = logging.getLogger(__name__)
console = Console()

def parse_arguments() -> argparse.Namespace:
    """
    Parses and configures the CLI arguments for the bot.
    """
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet USDT-M Trading Bot CLI tool.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="The futures trading pair to order (e.g., BTCUSDT, ETHUSDT)."
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=["BUY", "SELL"],
        help="The direction of the order (BUY or SELL)."
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=["MARKET", "LIMIT"],
        help="The order type: MARKET or LIMIT."
    )
    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
        help="The amount/size of the asset to order (e.g., 0.001)."
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="The price at which to execute the limit order. Required for LIMIT orders."
    )
    
    return parser.parse_args()

def run_cli() -> None:
    """
    Executes the main workflow of the trading bot CLI:
    Config loading, CLI parsing, validation, client initialization, and order dispatching.
    """
    # Initialize the structured logger
    setup_logging()
    
    # Parse CLI input
    args = parse_arguments()
    
    # Standardize inputs to uppercase strings
    symbol = args.symbol.strip().upper()
    side = args.side.strip().upper()
    order_type = args.type.strip().upper()
    quantity = args.quantity
    price = args.price

    # Validate the input variables
    try:
        validate_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
    except ValueError as e:
        console.print(f"\n[bold red][Input Validation Error][/bold red] {e}\n")
        logger.error("Validation failed: %s", e)
        sys.exit(1)

    # Check environment configuration
    try:
        config.validate_config()
    except ValueError as e:
        console.print(f"\n[bold red][Configuration Error][/bold red] {e}\n")
        logger.error("Configuration failed: %s", e)
        sys.exit(1)

    # Render Order Summary panel for validation visibility
    summary_table = Table(box=box.SIMPLE_HEAD, show_header=False, min_width=40)
    summary_table.add_column("Parameter", style="cyan bold")
    summary_table.add_column("Value", style="magenta")
    summary_table.add_row("Symbol", symbol)
    summary_table.add_row("Side", side)
    summary_table.add_row("Type", order_type)
    summary_table.add_row("Quantity", str(quantity))
    if price is not None:
        summary_table.add_row("Price", f"${price:,.2f}")
        
    console.print(
        Panel(
            summary_table,
            title="[bold yellow]Order Parameters[/bold yellow]",
            border_style="yellow",
            expand=False
        )
    )
    
    logger.info(
        "Order request submitted - Symbol: %s, Side: %s, Type: %s, Qty: %s, Price: %s",
        symbol, side, order_type, quantity, price
    )

    # Initialize client and submit the order
    client = BinanceFuturesClient(
        api_key=config.BINANCE_API_KEY,
        secret_key=config.BINANCE_SECRET_KEY,
        base_url=config.BASE_URL
    )
    
    with client:
        try:
            # Interactive status loading
            with console.status("[bold green]Transmitting order to Binance Testnet REST API...[/bold green]"):
                if order_type == "MARKET":
                    order_result = place_market_order(
                        client=client,
                        symbol=symbol,
                        side=side,
                        quantity=quantity
                    )
                else:
                    assert price is not None  # Validated earlier
                    order_result = place_limit_order(
                        client=client,
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        price=price
                    )
            
            logger.info("Order placed successfully. ID: %s", order_result.get("order_id"))
            
            # Format results in a beautiful Rich Table
            result_table = Table(box=box.ROUNDED, header_style="bold cyan", min_width=50)
            result_table.add_column("Key", style="dim")
            result_table.add_column("Value")
            
            for key, val in order_result.items():
                formatted_key = key.replace("_", " ").title()
                formatted_val = str(val)
                
                # Dynamic highlighting based on response state
                if key == "status":
                    if val in ["NEW", "FILLED"]:
                        formatted_val = f"[bold green]{val}[/bold green]"
                    else:
                        formatted_val = f"[bold yellow]{val}[/bold yellow]"
                elif key == "side":
                    formatted_val = f"[bold green]{val}[/bold green]" if val == "BUY" else f"[bold red]{val}[/bold red]"
                elif key == "price" or key == "average_price" or key == "cum_quote":
                    formatted_val = f"${to_float(val):,.4f}" if to_float(val) > 0 else "-"
                
                result_table.add_row(formatted_key, formatted_val)
                
            console.print(
                Panel(
                    result_table,
                    title="[bold green]Order Executed Successfully[/bold green]",
                    border_style="green",
                    expand=False
                )
            )
            
        except BinanceClientError as e:
            console.print(f"\n[bold red][Execution Failure][/bold red] {e}\n")
            logger.error("Order execution failed: %s", e)
            sys.exit(1)

def to_float(val: Any) -> float:
    """Helper to convert response values for output representation."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0
