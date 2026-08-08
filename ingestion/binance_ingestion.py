from connectors.binance_connector import BinanceConnector
from storage.local_storage import LocalStorage
from storage.s3_storage import S3Storage


# Get data from Binance
connector = BinanceConnector()

account_data = connector.get_account()


# Save data locally
storage = LocalStorage()

file_path = storage.save_json(
    account_data,
    source="binance",
    data_type="account"
)

print("Saved to:", file_path)


# Upload the same file to S3
s3_storage = S3Storage()

s3_key = str(file_path).replace("\\", "/")

s3_storage.upload_file(
    file_path,
    s3_key
)