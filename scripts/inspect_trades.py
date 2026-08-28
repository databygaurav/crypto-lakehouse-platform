from clients.binance_client import BinanceClient


client = BinanceClient()

trading_pairs = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "SUIUSDT",
    "LINKUSDT",
    "ONDOUSDT",
]


for pair in trading_pairs:
    print(f"\nGetting trades for {pair}...")

    trades = client.get_trades(pair)

    print(f"{pair}: {len(trades)} trades found")
