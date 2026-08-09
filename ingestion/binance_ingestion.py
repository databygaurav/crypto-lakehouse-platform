from connectors.binance_connector import BinanceConnector
from storage.local_storage import LocalStorage
from storage.s3_storage import S3Storage


# Create our components
connector = BinanceConnector()
local_storage = LocalStorage()
s3_storage = S3Storage()


# -------------------------
# 1. Get account data
# -------------------------

account_data = connector.get_account()

account_file = local_storage.save_json(
    account_data,
    source="binance",
    data_type="account"
)

print("Account saved to:", account_file)


# Upload account data to S3
account_s3_key = str(account_file).replace("\\", "/")

s3_storage.upload_file(
    account_file,
    account_s3_key
)


# -------------------------
# 2. Get BTCUSDT trades
# -------------------------

trades = connector.get_trades("BTCUSDT")

trade_file = local_storage.save_json(
    trades,
    source="binance",
    data_type="trades"
)

print("Trades saved to:", trade_file)


# Upload trades to S3
trade_s3_key = str(trade_file).replace("\\", "/")

s3_storage.upload_file(
    trade_file,
    trade_s3_key
)


print("Ingestion completed successfully!")