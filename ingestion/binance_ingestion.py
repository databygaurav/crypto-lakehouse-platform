from datetime import datetime, timezone

from connectors.binance_connector import BinanceConnector
from storage.local_storage import LocalStorage
from storage.s3_storage import S3Storage


# ============================================================
# CONFIGURATION
# ============================================================

TRADING_PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "SUIUSDT",
    "LINKUSDT",
    "ONDOUSDT",
]


# Historical P2P range
# January 1, 2026
P2P_START_TIMESTAMP = 1767225600000

# Current date/time
P2P_END_TIMESTAMP = int(
    datetime.now(timezone.utc).timestamp() * 1000
)


# ============================================================
# CREATE COMPONENTS
# ============================================================

connector = BinanceConnector()
local_storage = LocalStorage()
s3_storage = S3Storage()


# ============================================================
# 1. ACCOUNT
# ============================================================

print("\nGetting Binance account...")

account_data = connector.get_account()

account_file = local_storage.save_json(
    account_data,
    source="binance",
    data_type="account"
)

print("Account saved to:", account_file)


account_s3_key = str(account_file).replace("\\", "/")

s3_storage.upload_file(
    account_file,
    account_s3_key
)


# ============================================================
# 2. SPOT TRADES
# ============================================================

for pair in TRADING_PAIRS:

    print(f"\nGetting trades for {pair}...")

    trades = connector.get_trades(pair)

    trade_file = local_storage.save_json(
        trades,
        source="binance",
        data_type="trades",
        symbol=pair
    )

    print("Trades saved to:", trade_file)

    trade_s3_key = str(trade_file).replace("\\", "/")

    s3_storage.upload_file(
        trade_file,
        trade_s3_key
    )


# ============================================================
# 3. P2P BUY TRANSACTIONS
# ============================================================

print("\nGetting Binance P2P BUY transactions...")

p2p_buy_data = connector.get_p2p_transactions(
    trade_type="BUY",
    page=1,
    rows=100,
    start_timestamp=P2P_START_TIMESTAMP,
    end_timestamp=P2P_END_TIMESTAMP
)

p2p_buy_records = p2p_buy_data.get("data", [])

print(
    f"P2P BUY transactions received: "
    f"{len(p2p_buy_records)}"
)


p2p_buy_file = local_storage.save_json(
    p2p_buy_data,
    source="binance",
    data_type="p2p_buy"
)

print("P2P BUY saved to:", p2p_buy_file)


p2p_buy_s3_key = str(p2p_buy_file).replace("\\", "/")

s3_storage.upload_file(
    p2p_buy_file,
    p2p_buy_s3_key
)


# ============================================================
# 4. P2P SELL TRANSACTIONS
# ============================================================

print("\nGetting Binance P2P SELL transactions...")

p2p_sell_data = connector.get_p2p_transactions(
    trade_type="SELL",
    page=1,
    rows=100,
    start_timestamp=P2P_START_TIMESTAMP,
    end_timestamp=P2P_END_TIMESTAMP
)

p2p_sell_records = p2p_sell_data.get("data", [])

print(
    f"P2P SELL transactions received: "
    f"{len(p2p_sell_records)}"
)


p2p_sell_file = local_storage.save_json(
    p2p_sell_data,
    source="binance",
    data_type="p2p_sell"
)

print("P2P SELL saved to:", p2p_sell_file)


p2p_sell_s3_key = str(p2p_sell_file).replace("\\", "/")

s3_storage.upload_file(
    p2p_sell_file,
    p2p_sell_s3_key
)


# ============================================================
# COMPLETE
# ============================================================

print("\n========================================")
print("Ingestion completed successfully!")
print("========================================")