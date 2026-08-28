from storage.s3_storage import S3Storage

storage = S3Storage()

storage.upload_file(
    "data/raw/binance/account/year=2026/month=08/day=07/account_20260807_210836.json",
    "raw/binance/account/year=2026/month=08/day=07/account_20260807_210836.json"
)