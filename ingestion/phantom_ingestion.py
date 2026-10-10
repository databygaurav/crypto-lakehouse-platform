"""Download and save raw Phantom wallet data."""

import argparse
from datetime import datetime, timezone

from clients.phantom_client import PhantomClient
from storage.local_storage import LocalStorage
from storage.s3_storage import S3Storage


# ========================================================
# SAVE ONE RAW DATASET
# ========================================================

def save_raw_data(
    data,
    local_storage,
    s3_storage,
    data_type
):
    """Save Phantom data locally and optionally upload it to S3."""

    file_path = local_storage.save_json(
        data=data,
        source="phantom",
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


# ========================================================
# RUN PHANTOM INGESTION
# ========================================================

def run_ingestion(
    client=None,
    local_storage=None,
    s3_storage=None,
    upload_to_s3=True
):
    """Download and save Phantom wallet data."""

    client = (
        client
        or PhantomClient()
    )

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

    def save(
        name,
        data
    ):
        saved_files[name] = save_raw_data(
            data=data,
            local_storage=local_storage,
            s3_storage=s3_storage,
            data_type=name
        )

    # ========================================================
    # SOLANA
    # ========================================================

    print(
        "1. Downloading Phantom SOL balance..."
    )

    sol_balance = client.get_sol_balance()

    save(
        name="sol_balance",
        data=sol_balance
    )

    print(
        "2. Downloading Phantom SOL transactions..."
    )

    sol_transactions = (
        client.get_all_sol_transactions(
            limit=100
        )
    )

    save(
        name="sol_transactions",
        data=sol_transactions
    )

    # ========================================================
    # ETHEREUM
    # ========================================================

    """
    print(
        "3. Downloading Phantom ETH balance..."
    )

    eth_balance = client.get_eth_balance()

    save(
        name="eth_balance",
        data=eth_balance
    )

    print(
        "4. Downloading Phantom ETH transactions..."
    )

    eth_transactions = client.get_eth_transactions(
        limit=100
    )

    save(
        name="eth_transactions",
        data=eth_transactions
    )

    print(
        "5. Downloading Phantom ETH token transfers..."
    )

    eth_token_transfers = (
        client.get_eth_token_transfers(
            limit=100
        )
    )

    save(
        name="eth_token_transfers",
        data=eth_token_transfers
    )

    print(
        "6. Downloading tracked ETH token balances..."
    )

    eth_token_balances = (
        client.get_eth_token_balances()
    )

    save(
        name="eth_token_balances",
        data=eth_token_balances
    )
    """

    # ========================================================
    # SUI
    # ========================================================

    """
    print(
        "7. Downloading Phantom SUI balance..."
    )

    sui_balance = client.get_sui_balance()

    save(
        name="sui_balance",
        data=sui_balance
    )

    print(
        "8. Downloading Phantom SUI transactions..."
    )

    sui_transactions = client.get_sui_transactions(
        limit=100
    )

    save(
        name="sui_transactions",
        data=sui_transactions
    )
    """

    # ========================================================
    # BITCOIN
    # ========================================================

    """
    print(
        "9. Downloading Phantom BTC balance..."
    )

    btc_balance = client.get_btc_balance()

    save(
        name="btc_balance",
        data=btc_balance
    )

    print(
        "10. Downloading Phantom BTC transactions..."
    )

    btc_transactions = client.get_btc_transactions(
        limit=100
    )

    save(
        name="btc_transactions",
        data=btc_transactions
    )
    """

# ========================================================
# INGESTION MANIFEST
# ========================================================

    print(
        "3. Creating Phantom ingestion manifest..."
    )

    manifest = {
        "source": "phantom",
        "completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "files": {
            name: str(path)
            for name, path in saved_files.items()
        }
    }

    save(
        name="ingestion_manifest",
        data=manifest
    )

    return saved_files


# ========================================================
# TERMINAL COMMAND
# ========================================================

def main():
    """Read terminal options and start Phantom ingestion."""

    parser = argparse.ArgumentParser(
        description=(
            "Download raw Phantom wallet data"
        )
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