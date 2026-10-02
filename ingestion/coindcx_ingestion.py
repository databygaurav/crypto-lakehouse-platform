"""Download and save raw CoinDCX data."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from clients.coindcx_client import CoinDCXClient
from storage.local_storage import LocalStorage
from storage.s3_storage import S3Storage


REPORT_FOLDER = Path("raw report") / "coindcx"


def load_json(file_name):
    """Read one JSON file from the private report folder."""

    file_path = REPORT_FOLDER / file_name

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    return data

def save_raw_data(
    data,
    local_storage,
    s3_storage,
    data_type
):
    """Save data locally and optionally upload it to S3."""

    file_path = local_storage.save_json(
        data=data,
        source="coindcx",
        data_type=data_type
    )

    if s3_storage is not None:
        s3_storage.upload_file(
            local_file=file_path,
            s3_key=file_path.as_posix()
        )

    print(
        f"Saved {data_type}: {file_path}"
    )

    return file_path


def run_ingestion(
    client=None,
    local_storage=None,
    s3_storage=None,
    upload_to_s3=True
):
    """Load and save all raw CoinDCX data."""

    client = client or CoinDCXClient()
    local_storage = (
        local_storage
        or LocalStorage()
    )

    if upload_to_s3:
        s3_storage = (
            s3_storage
            or S3Storage()
        )
    else:
        s3_storage = None

    saved_files = {}

    print(
        "1. Downloading CoinDCX balances..."
    )

    balances = client.get_balances()

    saved_files["balances"] = (
        save_raw_data(
            data=balances,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type="balances"
        )
    )

    print(
        "2. Reading CoinDCX Instant orders..."
    )

    instant_orders = load_json(
        "coindcx_instant_orders.json"
    )

    saved_files["instant_orders"] = (
        save_raw_data(
            data=instant_orders,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type="instant_orders"
        )
    )

    print(
        "3. Reading CoinDCX fiat deposits..."
    )

    fiat_deposits = load_json(
        "coindcx_fiat_deposits.json"
    )

    saved_files["fiat_deposits"] = (
        save_raw_data(
            data=fiat_deposits,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type="fiat_deposits"
        )
    )

    print(
        "4. Reading CoinDCX fiat withdrawals..."
    )

    fiat_withdrawals = load_json(
        "coindcx_fiat_withdrawals.json"
    )

    saved_files["fiat_withdrawals"] = (
        save_raw_data(
            data=fiat_withdrawals,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type="fiat_withdrawals"
        )
    )

    print(
        "5. Reading CoinDCX crypto deposits..."
    )

    crypto_deposits = load_json(
        "coindcx_crypto_deposits.json"
    )

    saved_files["crypto_deposits"] = (
        save_raw_data(
            data=crypto_deposits,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type="crypto_deposits"
        )
    )

    print(
        "6. Reading CoinDCX crypto withdrawals..."
    )

    crypto_withdrawals = load_json(
        "coindcx_crypto_withdrawals.json"
    )

    saved_files["crypto_withdrawals"] = (
        save_raw_data(
            data=crypto_withdrawals,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type="crypto_withdrawals"
        )
    )

    print(
        "7. Creating ingestion manifest..."
    )

    manifest = {
        "source": "coindcx",
        "completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "files": {
            name: str(path)
            for name, path
            in saved_files.items()
        }
    }

    saved_files["ingestion_manifest"] = (
        save_raw_data(
            data=manifest,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type="ingestion_manifest"
        )
    )

    return saved_files

def main():
    """Read terminal options and start CoinDCX ingestion."""

    parser = argparse.ArgumentParser(
        description="Download raw CoinDCX data"
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
