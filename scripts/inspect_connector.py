from clients.binance_client import BinanceClient

client = BinanceClient()

account = client.get_account()

print("Account response fields:", sorted(account))
print("Balance records:", len(account.get("balances", [])))
