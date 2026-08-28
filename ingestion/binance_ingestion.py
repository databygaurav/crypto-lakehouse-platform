"""Download raw Binance data and save it locally and optionally to S3."""

import argparse
from datetime import datetime, timedelta, timezone

from clients.binance_client import BinanceClient
from config.settings import BINANCE_HISTORY_START
from storage.local_storage import LocalStorage
from storage.s3_storage import S3Storage
from utils.history_fetcher import fetch_klines_history


# Edit these lists when you want to collect another trading pair or transfer type.
TRADING_PAIRS = (
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "SUIUSDT",
    "LINKUSDT",
    "ONDOUSDT",
)

TRANSFER_TYPES = (
    "MAIN_UMFUTURE",
)

PRICE_INTERVAL = "1d"


def save_raw_data(
    data,
    local_storage,
    s3_storage,
    data_type,
    symbol=None,
):
    """Save one raw API response locally, then optionally upload it to S3."""

    file_path = local_storage.save_json(
        data=data,
        source="binance",
        data_type=data_type,
        symbol=symbol,
    )

    if s3_storage is not None:
        s3_storage.upload_file(
            local_file=file_path,
            s3_key=file_path.as_posix(),
        )

    print(f"Saved {data_type}: {file_path}")
    return file_path


def get_price_history(client, symbol, start_time, end_time):
    """Download all daily price candles for one trading pair."""

    return fetch_klines_history(
        get_klines=client.get_klines,
        symbol=symbol,
        interval=PRICE_INTERVAL,
        start_time=int(start_time.timestamp() * 1000),
        end_time=int(end_time.timestamp() * 1000),
        limit=1000,
    )


def run_ingestion(
    client=None,
    local_storage=None,
    s3_storage=None,
    history_start=BINANCE_HISTORY_START,
    history_end=None,
    trading_pairs=TRADING_PAIRS,
    transfer_types=TRANSFER_TYPES,
    upload_to_s3=True,
):
    """Run the complete raw-data ingestion pipeline.

    This function only downloads and stores raw data. It does not clean,
    transform, or aggregate the records.
    """

    history_end = history_end or datetime.now(timezone.utc)

    if history_start.tzinfo is None or history_end.tzinfo is None:
        raise ValueError("History dates must be timezone-aware")

    if history_start >= history_end:
        raise ValueError("history_start must be before history_end")

    client = client or BinanceClient()
    local_storage = local_storage or LocalStorage()

    if upload_to_s3:
        s3_storage = s3_storage or S3Storage()
    else:
        s3_storage = None

    saved_files = {}

    def save(name, data, symbol=None):
        """Short local helper that keeps the steps below easy to read."""

        saved_files[name] = save_raw_data(
            data=data,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type=name.split(":", 1)[0],
            symbol=symbol,
        )

    print("1. Downloading account snapshot...")
    save("account", client.get_account())

    print("2. Downloading Spot trades...")
    for symbol in trading_pairs:
        save(
            f"trades:{symbol}",
            client.get_all_trades(symbol=symbol),
            symbol=symbol,
        )

    print("3. Downloading Convert trades...")
    save(
        "convert_trades",
        client.get_all_convert_trades(
            start_datetime=history_start,
            end_datetime=history_end,
        ),
    )

    # Binance exposes P2P history for only the latest six months.
    p2p_start = max(
        history_start,
        history_end - timedelta(days=180),
    )

    print("4. Downloading P2P orders...")
    for trade_type in ("BUY", "SELL"):
        name = f"p2p_{trade_type.lower()}"
        save(
            name,
            client.get_all_p2p_transactions(
                trade_type=trade_type,
                start_datetime=p2p_start,
                end_datetime=history_end,
            ),
        )

    print("5. Downloading deposits and withdrawals...")
    save(
        "deposits",
        client.get_all_deposits(
            start_datetime=history_start,
            end_datetime=history_end,
        ),
    )
    save(
        "withdrawals",
        client.get_all_withdrawals(
            start_datetime=history_start,
            end_datetime=history_end,
        ),
    )

    print("6. Downloading account transfers...")
    for transfer_type in transfer_types:
        save(
            f"transfers:{transfer_type}",
            client.get_all_transfers(
                end_datetime=history_end,
                transfer_type=transfer_type,
            ),
            symbol=transfer_type,
        )

    print("7. Downloading daily price history...")
    for symbol in trading_pairs:
        prices = get_price_history(
            client=client,
            symbol=symbol,
            start_time=history_start,
            end_time=history_end,
        )

        if prices:
            save(
                f"price_history:{symbol}",
                prices,
                symbol=symbol,
            )
        else:
            print(f"No price history returned for {symbol}")

    manifest = {
        "source": "binance",
        "history_start": history_start.isoformat(),
        "history_end": history_end.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "files": {
            name: str(path)
            for name, path in saved_files.items()
        },
    }
    save("ingestion_manifest", manifest)

    return saved_files


def main():
    """Read command-line options and start ingestion."""

    parser = argparse.ArgumentParser(
        description="Download raw Binance data"
    )
    parser.add_argument(
        "--local-only",
        "--no-s3",
        action="store_true",
        dest="local_only",
        help="Save locally without uploading to S3",
    )
    args = parser.parse_args()

    files = run_ingestion(
        upload_to_s3=not args.local_only
    )
    print(f"Done. Saved {len(files)} raw datasets.")


if __name__ == "__main__":
    main()
