from datetime import datetime, timezone

from clients.binance_client import BinanceClient

from config.settings import (
    BINANCE_HISTORY_START
)


# ============================================================
# CONNECTOR
# ============================================================

client = BinanceClient()


# ============================================================
# DATES
# ============================================================

START_DATE = BINANCE_HISTORY_START

END_DATE = datetime.now(
    timezone.utc
)


# ============================================================
# HEADER
# ============================================================

print("\n")
print("=" * 70)
print("BINANCE TRANSACTION HISTORY")
print("=" * 70)

print(
    f"\nGeneral history start:"
    f" {START_DATE}"
)

print(
    f"End date:"
    f" {END_DATE}"
)


# ============================================================
# DEPOSITS
# ============================================================

print("\n")
print("=" * 70)
print("DEPOSIT HISTORY")
print("=" * 70)


deposits = client.get_all_deposits(
    start_datetime=START_DATE,
    end_datetime=END_DATE
)


print(
    f"\nTotal deposits: "
    f"{len(deposits)}"
)


for deposit in deposits:

    print(
        "\n"
        f"Coin: "
        f"{deposit.get('coin')}\n"

        f"Amount: "
        f"{deposit.get('amount')}\n"

        f"Network: "
        f"{deposit.get('network')}\n"

        f"Status: "
        f"{deposit.get('status')}\n"

        f"TxID: "
        f"{deposit.get('txId')}\n"

        f"Address: "
        f"{deposit.get('address')}\n"

        f"Insert Time: "
        f"{deposit.get('insertTime')}"
    )


# ============================================================
# WITHDRAWALS
# ============================================================

print("\n")
print("=" * 70)
print("WITHDRAWAL HISTORY")
print("=" * 70)


withdrawals = client.get_all_withdrawals(
    start_datetime=START_DATE,
    end_datetime=END_DATE
)


print(
    f"\nTotal withdrawals: "
    f"{len(withdrawals)}"
)


for withdrawal in withdrawals:

    print(
        "\n"
        f"Coin: "
        f"{withdrawal.get('coin')}\n"

        f"Amount: "
        f"{withdrawal.get('amount')}\n"

        f"Network: "
        f"{withdrawal.get('network')}\n"

        f"Status: "
        f"{withdrawal.get('status')}\n"

        f"TxID: "
        f"{withdrawal.get('txId')}\n"

        f"Address: "
        f"{withdrawal.get('address')}\n"

        f"Apply Time: "
        f"{withdrawal.get('applyTime')}"
    )


# ============================================================
# UNIVERSAL TRANSFERS
# ============================================================

print("\n")
print("=" * 70)
print("UNIVERSAL TRANSFER HISTORY")
print("=" * 70)


# ------------------------------------------------------------
# IMPORTANT
#
# This is ONE Binance transfer category.
#
# We will test the categories individually before
# putting them into production ingestion.
# ------------------------------------------------------------

TRANSFER_TYPE = "MAIN_UMFUTURE"


transfers = client.get_all_transfers(
    end_datetime=END_DATE,
    transfer_type=TRANSFER_TYPE
)


print(
    f"\nTransfer type:"
    f" {TRANSFER_TYPE}"
)

print(
    f"Total transfers:"
    f" {len(transfers)}"
)


for transfer in transfers:

    print(
        "\n"
        f"Transfer Type: "
        f"{transfer.get('transferType')}\n"

        f"Asset: "
        f"{transfer.get('asset')}\n"

        f"Amount: "
        f"{transfer.get('amount')}\n"

        f"Status: "
        f"{transfer.get('status')}\n"

        f"Transaction ID: "
        f"{transfer.get('tranId')}\n"

        f"Timestamp: "
        f"{transfer.get('timestamp')}"
    )


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(
    f"Deposits:    {len(deposits)}"
)

print(
    f"Withdrawals: {len(withdrawals)}"
)

print(
    f"Transfers:   {len(transfers)}"
)

print("=" * 70)
print("TEST COMPLETED")
print("=" * 70)
