from connectors.binance_connector import BinanceConnector
from storage.local_storage import LocalStorage


connector = BinanceConnector()

account = connector.get_account()

storage = LocalStorage()

file_path = storage.save_json(
    account,
    source="binance",
    data_type="account"
)

print("Saved to:", file_path)
