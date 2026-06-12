# Binance Futures Testnet Trading Bot

A clean, production-ready, fully typed CLI application for executing `MARKET` and `LIMIT` orders on the **Binance Futures Testnet (USDT-M)**.

Built using **Python 3.11** and direct REST API calls using `httpx` (avoiding wrapper libraries like `python-binance`), it demonstrates standard HMAC-SHA256 signature payload authentication, strict validators, dual-stream structured logging, and a premium command-line user interface using `rich`.

---

## Architecture Overview

The codebase is built with modularity, clean separation of concerns, and type-safety in mind:

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package initialization
│   ├── client.py            # Core signed REST client (HMAC-SHA256, connection pooling)
│   ├── orders.py            # Normalized order handlers (MARKET & LIMIT)
│   ├── validators.py        # Input rules validation layer
│   ├── logging_config.py    # Dual logger layout (structured file & clean console)
│   ├── config.py            # Environment validation & dotenv configuration
│   └── cli.py               # User terminal interface & rich output formatting
├── logs/
│   └── trading.log          # Detailed historical log file (auto-generated)
├── .env.example             # Configuration placeholders
├── requirements.txt         # Package dependencies with exact version limits
├── README.md                # Project documentation
└── main.py                  # Entry point script
```

- **Client Layer (`client.py`)**: Direct communication via `httpx.Client`. Manages local signature encoding matching Binance API signing standard (HMAC SHA256) and parses raw network/status issues into clean exceptions.
- **Validation Layer (`validators.py`)**: Validates input bounds strictly (e.g., non-empty uppercase symbols, valid quantity float, price matching rules relative to order types) and triggers descriptive exceptions prior to hit execution.
- **Logging Layer (`logging_config.py`)**: Implements verbose debugging traces into `logs/trading.log` while displaying short, human-readable statements on standard stdout console streams.

---

## Getting Started

### 1. Prerequisites
- Python 3.11 installed on your local system.

### 2. Installation
Clone this repository (or copy the folder), navigate to the root directory, and install requirements:

```bash
# Navigate to the root project directory
cd trading_bot

# Install the dependencies
pip install -r requirements.txt
```

### 3. Generate Binance Testnet Keys
1. Go to the [Binance Futures Testnet Web Platform](https://testnet.binancefuture.com) and log in or create a mock account.
2. In the bottom dashboard, under the **API Key** tab, click **Register Testnet API Key**.
3. Generate your Key Pair, copy the `API Key` and the `Secret Key` (ensure you keep them private).

### 4. Configure Environment
Duplicate the `.env.example` file and create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Open `.env` and paste your credentials:
```env
BINANCE_API_KEY=your_actual_testnet_api_key_here
BINANCE_SECRET_KEY=your_actual_testnet_secret_key_here
BASE_URL=https://testnet.binancefuture.com
```

---

## Usage & Execution Examples

The bot supports command line flags to submit orders. Below are examples of how to execute calls:

### Place a MARKET Buy Order
```bash
python main.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

### Place a LIMIT Sell Order
```bash
python main.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000
```

---

## Sample Console Output

When executing commands successfully, you will see a polished output like the following:

```
┌──────────────────────────────────────┐
│           Order Parameters           │
├──────────────────────────────────────┤
│ Symbol   BTCUSDT                     │
│ Side     BUY                         │
│ Type     LIMIT                       │
│ Quantity 0.001                       │
│ Price    $98,500.00                  │
└──────────────────────────────────────┘
 ⠋ Transmitting order to Binance Testnet REST API...

┌──────────────────────────────────────────────────┐
│             ✓ Order Executed Successfully        │
├──────────────────────────────────────────────────┤
│ Order Id          22547492982                    │
│ Client Order Id   x-3OP45WQM                     │
│ Symbol            BTCUSDT                        │
│ Status            NEW                            │
│ Side              BUY                            │
│ Type              LIMIT                          │
│ Quantity          0.001                          │
│ Executed Quantity 0.0                            │
│ Price             $98,500.0000                   │
│ Average Price     -                              │
│ Time In Force     GTC                            │
│ Cum Quote         -                              │
│ Update Time       1718205229000                  │
└──────────────────────────────────────────────────┘
```

---

## Assumptions & Design Choices

1. **Time In Force (TIF)**: For limit orders, Binance Futures requires a TIF policy. This implementation defaults to `GTC` (Good 'Til Cancelled), as it's the standard expected for typical entry limit executions.
2. **Precision Bounds**: Prices and quantities are passed to the API as string representations to avoid floating-point rounding precision issues that can cause Binance API to reject inputs.
3. **Dual Stream Logs**: `stdout` logging provides clean updates to the CLI user interface, whereas `logs/trading.log` provides detailed debug traces containing exact request payload details, sign inputs, and response payloads for quick post-mortem analyses.
