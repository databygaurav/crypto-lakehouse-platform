"""Test the read-only Phantom wallet client."""

from datetime import datetime, timezone
from pprint import pprint

from clients.phantom_client import PhantomClient


client = PhantomClient()

"""
# ========================================================
# TEST PHANTOM SOL BALANCE
# ========================================================

sol_balance = client.get_sol_balance()

print()
print("PHANTOM SOL BALANCE")
print(sol_balance)


# ========================================================
# TEST PHANTOM SOL TRANSACTIONS
# ========================================================

sol_transactions = (
    client.get_all_sol_transactions()
)

print()
print(
    "TOTAL SOL TRANSACTIONS:",
    len(sol_transactions)
)

for record in sol_transactions:

    signature = record["signature"]
    transaction = record["transaction"]

    metadata = (
        transaction.get("meta")
        or {}
    )

    message = (
        transaction["transaction"]["message"]
    )

    error = metadata.get("err")
    block_time = transaction.get("blockTime")

    transaction_date = (
        datetime.fromtimestamp(
            block_time,
            tz=timezone.utc
        )
        .isoformat()
    )

    account_keys = message["accountKeys"]

    wallet_index = None
    fee_payer_address = None

    for index, account in enumerate(
        account_keys
    ):

        if isinstance(account, dict):
            account_address = account["pubkey"]
        else:
            account_address = account

        if index == 0:
            fee_payer_address = account_address

        if (
            account_address
            == client.solana_address
        ):
            wallet_index = index

    if wallet_index is None:
        continue

    before_lamports = metadata[
        "preBalances"
    ][wallet_index]

    after_lamports = metadata[
        "postBalances"
    ][wallet_index]

    balance_change_sol = (
        after_lamports
        - before_lamports
    ) / 1_000_000_000

    transaction_fee_sol = (
        metadata.get("fee", 0)
        / 1_000_000_000
    )

    phantom_paid_fee = (
        fee_payer_address
        == client.solana_address
    )

    if phantom_paid_fee:
        wallet_fee_sol = transaction_fee_sol
    else:
        wallet_fee_sol = 0

    if error is not None:

        direction = "FAILED"
        transfer_amount = 0

    elif balance_change_sol > 0:

        direction = "IN"
        transfer_amount = balance_change_sol

        if transfer_amount <= 0.000000001:
            direction = "DUST IN"

    elif balance_change_sol < 0:

        direction = "OUT"

        transfer_amount = (
            abs(balance_change_sol)
            - wallet_fee_sol
        )

    else:

        direction = "NO CHANGE"
        transfer_amount = 0

    print()
    print("Date:", transaction_date)
    print("Direction:", direction)
    print(
        "Transfer amount:",
        transfer_amount,
        "SOL"
    )
    print(
        "Wallet balance change:",
        balance_change_sol,
        "SOL"
    )
    print(
        "Wallet-paid fee:",
        wallet_fee_sol,
        "SOL"
    )
    print("Error:", error)
    print("Signature:", signature)


# ========================================================
# PUBLIC ETH ADDRESS USED ONLY FOR TESTING
# ========================================================

TEST_ETH_ADDRESS = (
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
)


# ========================================================
# TEST ETH BALANCE
# ========================================================

eth_balance = client.get_eth_balance(
    wallet_address=TEST_ETH_ADDRESS
)

print()
print("TEST ETH BALANCE")
print(eth_balance)


# ========================================================
# TEST NATIVE ETH TRANSACTIONS
# ========================================================

eth_transactions = (
    client.get_eth_transactions(
        wallet_address=TEST_ETH_ADDRESS,
        limit=5
    )
)

print()
print(
    "TEST ETH TRANSACTIONS:",
    len(eth_transactions)
)

for transaction in eth_transactions:

    sender = transaction["from"].lower()

    receiver = (
        transaction.get("to")
        or ""
    ).lower()

    wallet_address = (
        TEST_ETH_ADDRESS.lower()
    )

    timestamp = int(
        transaction["timestamp"],
        16
    )

    transaction_date = (
        datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc
        )
        .isoformat()
    )

    amount_wei = int(
        transaction["value"],
        16
    )

    amount_eth = (
        amount_wei
        / 1_000_000_000_000_000_000
    )

    gas_used = int(
        transaction["gasUsed"],
        16
    )

    gas_price = int(
        transaction["gasPrice"],
        16
    )

    transaction_fee_eth = (
        gas_used
        * gas_price
        / 1_000_000_000_000_000_000
    )

    if sender == wallet_address:

        direction = "OUT"
        wallet_fee_eth = transaction_fee_eth

    elif receiver == wallet_address:

        direction = "IN"
        wallet_fee_eth = 0

    else:

        direction = "UNKNOWN"
        wallet_fee_eth = 0

    if int(transaction["status"], 16) == 1:
        status = "SUCCESS"
    else:
        status = "FAILED"

    print()
    print("Date:", transaction_date)
    print("Direction:", direction)
    print(
        "Native amount:",
        amount_eth,
        "ETH"
    )
    print(
        "Wallet-paid fee:",
        wallet_fee_eth,
        "ETH"
    )
    print("Status:", status)
    print("Hash:", transaction["hash"])


# ========================================================
# TEST ERC-20 TOKEN TRANSFERS
# ========================================================

token_transfers = (
    client.get_eth_token_transfers(
        wallet_address=TEST_ETH_ADDRESS,
        limit=5
    )
)

print()
print(
    "TEST ETH TOKEN TRANSFERS:",
    len(token_transfers)
)

for token_transfer in token_transfers:

    print()
    pprint(token_transfer)

# ========================================================
# TEST ETH TOKEN BALANCES
# ========================================================

token_balances = (
    client.get_eth_token_balances(
        wallet_address=TEST_ETH_ADDRESS
    )
)

print()
print(
    "TRACKED ETH TOKEN BALANCES:",
    len(token_balances)
)

for token_balance in token_balances:
    pprint(token_balance)

# ========================================================
# TEST SUI BALANCE
# ========================================================

sui_response = client.get_sui_balance()

print()
print("RAW SUI RESPONSE")
print(sui_response)


print()
print("RAW SUI TRANSACTIONS")

sui_transactions = client.get_sui_transactions(
    limit=10
)

print(sui_transactions)"""

# ========================================================
# TEST BITCOIN BALANCE
# ========================================================

print()
print("PHANTOM BTC BALANCE")

btc_balance = client.get_btc_balance()

print(btc_balance)


# ========================================================
# TEST BITCOIN TRANSACTIONS
# ========================================================

print()
print("PHANTOM BTC TRANSACTIONS")

btc_transactions = client.get_btc_transactions(
    limit=10
)

print(
    "Total Bitcoin transactions:",
    len(btc_transactions)
)

print(btc_transactions)