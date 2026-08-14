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


# Historical start date
# January 1, 2026

HISTORY_START = datetime(
    2026,
    1,
    1,
    tzinfo=timezone.utc
)


# Current date/time

HISTORY_END = datetime.now(
    timezone.utc
)


# P2P API timestamps

P2P_START_TIMESTAMP = int(
    HISTORY_START.timestamp() * 1000
)

P2P_END_TIMESTAMP = int(
    HISTORY_END.timestamp() * 1000
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

print(
    "Account saved to:",
    account_file
)

account_s3_key = str(
    account_file
).replace("\\", "/")

s3_storage.upload_file(
    account_file,
    account_s3_key
)


# ============================================================
# 2. SPOT TRADES
# ============================================================

for pair in TRADING_PAIRS:

    print(
        f"\nGetting trades for {pair}..."
    )

    trades = connector.get_trades(
        pair
    )

    trade_file = local_storage.save_json(
        trades,
        source="binance",
        data_type="trades",
        symbol=pair
    )

    print(
        "Trades saved to:",
        trade_file
    )

    trade_s3_key = str(
        trade_file
    ).replace("\\", "/")

    s3_storage.upload_file(
        trade_file,
        trade_s3_key
    )


# ============================================================
# 3. P2P BUY
# ============================================================

print(
    "\nGetting Binance P2P BUY transactions..."
)

p2p_buy_data = connector.get_p2p_transactions(
    trade_type="BUY",
    page=1,
    rows=100,
    start_timestamp=P2P_START_TIMESTAMP,
    end_timestamp=P2P_END_TIMESTAMP
)

p2p_buy_records = p2p_buy_data.get(
    "data",
    []
)

print(
    "P2P BUY transactions received:",
    len(p2p_buy_records)
)

p2p_buy_file = local_storage.save_json(
    p2p_buy_data,
    source="binance",
    data_type="p2p_buy"
)

print(
    "P2P BUY saved to:",
    p2p_buy_file
)

p2p_buy_s3_key = str(
    p2p_buy_file
).replace("\\", "/")

s3_storage.upload_file(
    p2p_buy_file,
    p2p_buy_s3_key
)


# ============================================================
# 4. P2P SELL
# ============================================================

print(
    "\nGetting Binance P2P SELL transactions..."
)

p2p_sell_data = connector.get_p2p_transactions(
    trade_type="SELL",
    page=1,
    rows=100,
    start_timestamp=P2P_START_TIMESTAMP,
    end_timestamp=P2P_END_TIMESTAMP
)

p2p_sell_records = p2p_sell_data.get(
    "data",
    []
)

print(
    "P2P SELL transactions received:",
    len(p2p_sell_records)
)

p2p_sell_file = local_storage.save_json(
    p2p_sell_data,
    source="binance",
    data_type="p2p_sell"
)

print(
    "P2P SELL saved to:",
    p2p_sell_file
)

p2p_sell_s3_key = str(
    p2p_sell_file
).replace("\\", "/")

s3_storage.upload_file(
    p2p_sell_file,
    p2p_sell_s3_key
)


# ============================================================
# 5. DEPOSIT HISTORY
# ============================================================

print(
    "\nGetting Binance deposit history..."
)

deposits = connector.get_all_deposits(
    start_datetime=HISTORY_START,
    end_datetime=HISTORY_END
)

print(
    "Deposits received:",
    len(deposits)
)

deposit_file = local_storage.save_json(
    deposits,
    source="binance",
    data_type="deposits"
)

print(
    "Deposits saved to:",
    deposit_file
)

deposit_s3_key = str(
    deposit_file
).replace("\\", "/")

s3_storage.upload_file(
    deposit_file,
    deposit_s3_key
)


# ============================================================
# 6. WITHDRAWAL HISTORY
# ============================================================

print(
    "\nGetting Binance withdrawal history..."
)

withdrawals = connector.get_all_withdrawals(
    start_datetime=HISTORY_START,
    end_datetime=HISTORY_END
)

print(
    "Withdrawals received:",
    len(withdrawals)
)

withdrawal_file = local_storage.save_json(
    withdrawals,
    source="binance",
    data_type="withdrawals"
)

print(
    "Withdrawals saved to:",
    withdrawal_file
)

withdrawal_s3_key = str(
    withdrawal_file
).replace("\\", "/")

s3_storage.upload_file(
    withdrawal_file,
    withdrawal_s3_key
)


# ============================================================
# 7. INTERNAL TRANSFERS
# ============================================================

print(
    "\nGetting Binance internal transfers..."
)

# IMPORTANT:
# This is the transfer type we previously tested.
#
# MAIN_UMFUTURE =
# Binance Spot/Main Account
# ->
# USDⓈ-M Futures Account

TRANSFER_TYPE = "MAIN_UMFUTURE"


transfers = connector.get_all_transfers(
    end_datetime=HISTORY_END,
    transfer_type=TRANSFER_TYPE
)

print(
    "Internal transfers received:",
    len(transfers)
)

transfer_file = local_storage.save_json(
    transfers,
    source="binance",
    data_type="transfers"
)

print(
    "Transfers saved to:",
    transfer_file
)

transfer_s3_key = str(
    transfer_file
).replace("\\", "/")

s3_storage.upload_file(
    transfer_file,
    transfer_s3_key
)


# ============================================================
# COMPLETE
# ============================================================

print("\n========================================")
print("Binance ingestion completed successfully!")
print("========================================")