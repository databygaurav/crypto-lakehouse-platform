from pathlib import Path
from datetime import datetime

from processing.trade_processor import (
    load_trades,
    clean_trades,
    save_processed_trades,
)

from processing.parquet_writer import json_to_parquet

from storage.s3_storage import S3Storage


TRADES_PATH = Path("data/raw/binance/trades")


TRADING_PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "SUIUSDT",
    "LINKUSDT",
    "ONDOUSDT",
]


# Create S3 storage
s3_storage = S3Storage()


for pair in TRADING_PAIRS:

    print(f"\nProcessing {pair}...")

    pair_folder = TRADES_PATH / pair

    if not pair_folder.exists():
        print("Folder not found!")
        continue

    files = list(pair_folder.rglob("*.json"))

    if not files:
        print("No JSON files found!")
        continue

    # Find latest raw file
    latest_file = max(
        files,
        key=lambda file: file.stat().st_mtime
    )

    print("Reading:", latest_file)

    # -------------------------
    # 1. Load raw trades
    # -------------------------

    trades = load_trades(latest_file)

    print(f"Loaded {len(trades)} trades")

    # -------------------------
    # 2. Clean trades
    # -------------------------

    cleaned_trades = clean_trades(trades)

    # -------------------------
    # 3. Save processed JSON
    # -------------------------

    now = datetime.now()

    processed_folder = (
        Path("data/processed/binance/trades")
        / pair
        / f"year={now.year}"
        / f"month={now.month:02d}"
        / f"day={now.day:02d}"
    )

    processed_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    json_output = processed_folder / latest_file.name

    save_processed_trades(
        cleaned_trades,
        json_output
    )

    # -------------------------
    # 4. Upload processed JSON
    # -------------------------

    json_s3_key = str(json_output).replace("\\", "/")

    s3_storage.upload_file(
        json_output,
        json_s3_key
    )

    # -------------------------
    # 5. Convert JSON → Parquet
    # -------------------------

    parquet_output = processed_folder / (
        latest_file.stem + ".parquet"
    )

    json_to_parquet(
        json_output,
        parquet_output
    )

    # -------------------------
    # 6. Upload Parquet to S3
    # -------------------------

    parquet_s3_key = str(parquet_output).replace("\\", "/")

    s3_storage.upload_file(
        parquet_output,
        parquet_s3_key
    )


print("\nProcessing completed successfully!")