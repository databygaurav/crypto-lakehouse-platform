from datetime import datetime, timezone, timedelta

from clients.binance_client import BinanceClient

from utils.history_fetcher import (
    fetch_klines_history
)


# ============================================================
# CONFIGURATION
# ============================================================

SYMBOL = "BTCUSDT"

INTERVAL = "1d"


# ============================================================
# TIME RANGE
# ============================================================

END_TIME = datetime.now(
    timezone.utc
)

START_TIME = (
    END_TIME
    - timedelta(days=7)
)


START_MS = int(
    START_TIME.timestamp() * 1000
)

END_MS = int(
    END_TIME.timestamp() * 1000
)


# ============================================================
# CONNECTOR
# ============================================================

client = BinanceClient()


# ============================================================
# FETCH HISTORY
# ============================================================

print(
    f"Getting {SYMBOL} price history..."
)

klines = fetch_klines_history(
    get_klines=client.get_klines,
    symbol=SYMBOL,
    interval=INTERVAL,
    start_time=START_MS,
    end_time=END_MS,
    limit=1000
)


# ============================================================
# RESULTS
# ============================================================

print(
    f"\nTotal candles received: "
    f"{len(klines)}"
)

if klines:

    print(
        "\nFirst candle:"
    )

    print(
        klines[0]
    )

    print(
        "\nLast candle:"
    )

    print(
        klines[-1]
    )
