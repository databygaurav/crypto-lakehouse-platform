from clients.binance_client import BinanceClient


client = BinanceClient()


# ============================================================
# DATE RANGE
# ============================================================

# January 1, 2026
START_TIMESTAMP = 1767225600000

# August 12, 2026 23:59:59
END_TIMESTAMP = 1786550399999


# ============================================================
# BUY TRANSACTIONS
# ============================================================

print("=" * 70)
print("BUY P2P TRANSACTIONS")
print("=" * 70)

buy_data = client.get_p2p_transactions(
    trade_type="BUY",
    page=1,
    rows=100,
    start_timestamp=START_TIMESTAMP,
    end_timestamp=END_TIMESTAMP
)


print("\nAPI status:")
print(buy_data.get("code"))

print("\nMessage:")
print(buy_data.get("message"))

print("\nTotal BUY transactions:")
print(buy_data.get("total"))

buy_records = buy_data.get("data", [])

print("\nBUY records returned:")
print(len(buy_records))


for transaction in buy_records:

    print(
        f"\nOrder: {transaction.get('orderNumber')}"
        f"\nAsset: {transaction.get('asset')}"
        f"\nFiat: {transaction.get('fiat')}"
        f"\nType: {transaction.get('tradeType')}"
        f"\nAmount: {transaction.get('amount')}"
        f"\nINR Total: {transaction.get('totalPrice')}"
        f"\nPrice: {transaction.get('unitPrice')}"
        f"\nStatus: {transaction.get('orderStatus')}"
        f"\nPayment: {transaction.get('payMethodName')}"
    )


# ============================================================
# SELL TRANSACTIONS
# ============================================================

print("\n")
print("=" * 70)
print("SELL P2P TRANSACTIONS")
print("=" * 70)


sell_data = client.get_p2p_transactions(
    trade_type="SELL",
    page=1,
    rows=100,
    start_timestamp=START_TIMESTAMP,
    end_timestamp=END_TIMESTAMP
)


print("\nAPI status:")
print(sell_data.get("code"))

print("\nMessage:")
print(sell_data.get("message"))

print("\nTotal SELL transactions:")
print(sell_data.get("total"))

sell_records = sell_data.get("data", [])

print("\nSELL records returned:")
print(len(sell_records))


for transaction in sell_records:

    print(
        f"\nOrder: {transaction.get('orderNumber')}"
        f"\nAsset: {transaction.get('asset')}"
        f"\nFiat: {transaction.get('fiat')}"
        f"\nType: {transaction.get('tradeType')}"
        f"\nAmount: {transaction.get('amount')}"
        f"\nINR Total: {transaction.get('totalPrice')}"
        f"\nPrice: {transaction.get('unitPrice')}"
        f"\nStatus: {transaction.get('orderStatus')}"
        f"\nPayment: {transaction.get('payMethodName')}"
    )
