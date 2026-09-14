import argparse
from datetime import datetime, timezone
from clients.giottus_client import GiottusClient
from storage.local_storage import LocalStorage
from storage.s3_storage import S3Storage

TRADING_SYMBOLS = (
    "SOL/INR",
)

def save_raw_data(
    data,
    local_storage,
    s3_storage,
    data_type,
    symbol=None
):
    """Save Giottus data locally and optionally upload it to S3."""

    storage_symbol = None

    if symbol is not None:
        storage_symbol = symbol.replace("/", "")

    file_path = local_storage.save_json(
        data=data,
        source="giottus",
        data_type=data_type,
        symbol=storage_symbol
    )

    if s3_storage is not None:
        s3_storage.upload_file(
            local_file=file_path,
            s3_key=file_path.as_posix()
        )

    print(f"Saved {data_type}: {file_path}")

    return file_path

def run_ingestion(
    client=None,
    local_storage=None,
    s3_storage=None,
    trading_symbols=TRADING_SYMBOLS,
    upload_to_s3=True
):
    """Download and store raw Giottus data."""

    client = client or GiottusClient()
    local_storage = local_storage or LocalStorage()

    if upload_to_s3:
        s3_storage = s3_storage or S3Storage()
    else:
        s3_storage = None

    saved_files = {}

    def save(name, data, symbol=None):

        saved_files[name] = save_raw_data(
            data=data,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type=name.split(":", 1)[0],
            symbol=symbol
        )

    print("1. Downloading Giottus balances...")

    balances = client.get_balances()

    save(
        name="balances",
        data=balances
    )

    print("2 Downloading Giottus Spot trades...")

    for symbol in trading_symbols:

        trades = client.get_all_trades(
            symbol=symbol
        )

        save(
            name=f"trades:{symbol}",
            data=trades,
            symbol=symbol
        )
    
    print("3 Downloading Giottus EBES trades...")

    for symbol in trading_symbols:
         
        ebes_trades = client.get_all_ebes_trades(
            symbol=symbol
        )

        save(
            name=f"ebes_trades:{symbol}",
            data=ebes_trades,
            symbol=symbol
        )

    print("4 Downloading Giottus crypto deposits...")

    crypto_deposits = client.get_all_crypto_deposits()

    save(
        name="crypto_deposits",
        data=crypto_deposits
    )
    
    print("5. Downloading Giottus crypto withdrawals...")

    crypto_withdrawals = client.get_all_crypto_withdrawals()

    save(
        name="crypto_withdrawals",
        data=crypto_withdrawals
    )

    print("6. Downloading Giottus fiat deposits...")

    fiat_deposits = client.get_all_fiat_deposits()

    save(
        name="fiat_deposits",
        data=fiat_deposits
    )

    print("7. Downloading Giottus fiat withdrawals...")

    fiat_withdrawals = client.get_all_fiat_withdrawals()

    save(
        name="fiat_withdrawals",
        data=fiat_withdrawals
    )

    manifest = {
        "source": "giottus",
        "history_start": None,
        "history_end": None,
        "completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "files":{
            name: str(path)
            for name, path in saved_files.items()
        }
    }

    save(
        name="ingestion_manifest",
        data=manifest
    )

    return saved_files

def main():
    """Read terminal option and start Giottus ingestion."""

    parser = argparse.ArgumentParser(
        description="Download raw Giottus data"
    )

    parser.add_argument(
        "--local-only",
        "--no-s3",
        action="store_true",
        dest="local_only",
        help="Save locally without uploading to S3"
    )

    args = parser.parse_args()

    saved_files = run_ingestion(
        upload_to_s3=not args.local_only
    )

    print(
        f"Done. Saved {len(saved_files)} raw datasets."
    )


if __name__ == "__main__":
    main()