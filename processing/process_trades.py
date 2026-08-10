from pathlib import Path
from datetime import datetime
from processing.trade_processor import (
    load_trades,
    clean_trades,
    save_processed_trades,
)

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

    # Find the latest raw file
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
    # 3. Save processed file
    # -------------------------

    now = datetime.now()

    output_path = (
        Path("data/processed/binance/trades")
        / pair
        / f"year={now.year}"
        / f"month={now.month:02d}"
        / f"day={now.day:02d}"
        / latest_file.name
    )

    save_processed_trades(
        cleaned_trades,
        output_path
    )

    # -------------------------
    # 4. Upload processed file
    # -------------------------

    s3_key = str(output_path).replace("\\", "/")

    s3_storage.upload_file(
        output_path,
        s3_key
    )


print("\nProcessing completed successfully!")