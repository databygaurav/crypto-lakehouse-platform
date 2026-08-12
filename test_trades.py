from connectors.binance_connector import BinanceConnector


connector = BinanceConnector()

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

    trades = connector.get_trades(pair)

    print(f"{pair}: {len(trades)} trades found")