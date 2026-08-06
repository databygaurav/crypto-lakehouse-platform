from connectors.binance_connector import BinanceConnector

connector = BinanceConnector()

connector.authenticate()
connector.get_balances()
connector.get_trades()