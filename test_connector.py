from connectors.binance_connector import BinanceConnector

connector = BinanceConnector()

account = connector.get_account()

print(account)